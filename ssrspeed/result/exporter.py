import json
import os
import time

import requests
from loguru import logger
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji

from ssrspeed.config import ssrconfig
from ssrspeed.result.pusher import push2server
from ssrspeed.result.render import ExporterWps
from ssrspeed.result.sorter import Sorter

TMP_DIR = ssrconfig["path"]["tmp"]
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)
TEST_TXT = f"{TMP_DIR}test.txt"
LOGOS_DIR = ssrconfig["path"]["logos"]
RESULTS_DIR = ssrconfig["path"]["results"]
TEMPLATES_DIR = ssrconfig["path"]["templates"]

"""
resultJson
    {
        "group":"GroupName",
        "remarks":"Remarks",
        "loss":0,  # Data loss (0-1)
        "ping":0.014,
        "gping":0.011,
        "dspeed":12435646  # Bytes
        "maxDSpeed":12435646  # Bytes
    }
"""


class ExportResult:
    def __init__(self):
        self.__config: dict = ssrconfig["exportResult"]
        self.__addition: str = ssrconfig["exportResult"]["addition"]
        self.__hide_max_speed: bool = ssrconfig["exportResult"]["hide_max_speed"]
        self.__hide_ntt: bool = not ssrconfig["ntt"]["enabled"]
        self.__hide_geoip: bool = not ssrconfig["geoip"]
        self.__hide_ping: bool = not ssrconfig["ping"]
        self.__hide_gping: bool = not ssrconfig["gping"]
        self.__hide_stream: bool = not ssrconfig["stream"]
        self.__hide_netflix: bool = not ssrconfig["netflix"]
        self.__hide_bilibili = not ssrconfig["bilibili"]
        self.__hide_speed: bool = not ssrconfig["speed"]
        self.__test_method: bool = not ssrconfig["method"]
        self.__hide_stspeed: bool = not ssrconfig["StSpeed"]
        self.__hide_port: bool = not ssrconfig["port"]
        self.__hide_multiplex: bool = not ssrconfig["multiplex"]
        self.__colors: dict = {}
        self.__color_speed_list: list = []
        self.__font: ImageFont.FreeTypeFont = self.set_font(self.__config["font"])
        self.__time_used: str = "N/A"
        self.__upload_config: dict = ssrconfig["uploadResult"]

    # 	self.set_colors()

    def set_hide(self, **kwargs: bool):
        self.__hide_ntt = kwargs.get("ntt", True)
        self.__hide_geoip = kwargs.get("geoip", True)
        self.__hide_ping = kwargs.get("ping", True)
        self.__hide_gping = kwargs.get("gping", self.__hide_gping)
        self.__hide_stream = kwargs.get("stream", True)
        self.__hide_netflix = kwargs.get("netflix", self.__hide_netflix)
        self.__hide_bilibili = kwargs.get("bilibili", self.__hide_bilibili)
        self.__hide_speed = kwargs.get("speed", True)
        self.__hide_stspeed = kwargs.get("StSpeed", self.__hide_stspeed)
        self.__hide_port = kwargs.get("port", True)
        self.__hide_multiplex = kwargs.get("multiplex", True)

    def set_colors(self, name: str = "origin"):
        for color in self.__config["colors"]:
            if color["name"] == name:
                logger.info(f"Set colors as {name}.")
                self.__colors = color["colors"]
                self.__color_speed_list.append(0)
                for speed in self.__colors.keys():
                    try:
                        self.__color_speed_list.append(float(speed))
                    except Exception:
                        continue
                self.__color_speed_list.sort()
                return
        logger.warning(f"Color {name} not found in config.")

    @staticmethod
    def set_font(
        name: str = "SourceHanSansCN-Medium.otf", size: int = 18
    ) -> ImageFont.FreeTypeFont:
        font = ssrconfig["path"]["fonts"] + name
        custom_font = ssrconfig["path"]["custom"] + name
        if os.path.isfile(font):
            return ImageFont.truetype(font, size)
        if os.path.isfile(custom_font):
            return ImageFont.truetype(custom_font, size)
        raise FileNotFoundError(f"Font {name} not found.")

    def set_time_used(self, time_used: float):
        self.__time_used = time.strftime("%H:%M:%S", time.gmtime(time_used))
        logger.info(f"Time Used : {self.__time_used}")

    def export(self, result: list, export_type: int = 0, sort_method: str = ""):
        if not export_type:
            self.__export_as_json(result)
        sorter = Sorter()
        result = sorter.sort_result(result, sort_method)
        self.__export_as_png(result)

    def export_wps_result(self, result: list, export_type: int = 0):
        if not export_type:
            result = self.__export_as_json(result)
        epwps = ExporterWps(result, RESULTS_DIR, TEMPLATES_DIR)
        epwps.export()

    def __get_max_width(self, result: list) -> tuple:
        font = self.__font
        pilmoji = Pilmoji(Image.new("RGB", (1, 1), (255, 255, 255)))
        max_group_width = 0
        max_remark_width = 0
        len_in = 0
        len_out = 0
        for item in result:
            group = item["group"]
            remark = item["remarks"]
            inres = item["InRes"]
            outres = item["OutRes"]
            max_group_width = max(max_group_width, pilmoji.getsize(group, font=font)[0])
            max_remark_width = max(
                max_remark_width, pilmoji.getsize(remark, font=font)[0]
            )
            len_in = max(len_in, pilmoji.getsize(inres, font=font)[0])
            len_out = max(len_out, pilmoji.getsize(outres, font=font)[0])
        return max_group_width + 10, max_remark_width + 10, len_in + 20, len_out + 20

    def __get_base_pos(self, width: float, text: str) -> float:
        font = self.__font
        draw = ImageDraw.Draw(Image.new("RGB", (1, 1), (255, 255, 255)))
        text_size = draw.textsize(text, font=font)[0]
        base_pos = (width - text_size) / 2
        logger.debug(f"Base Position {base_pos}")
        return base_pos

    def __export_as_png(self, result: list):
        if not self.__color_speed_list:
            self.set_colors()
        result_font = self.__font
        generated_time = time.localtime()
        image_height = len(result) * 30 + 30
        weight = self.__get_max_width(result)
        group_width = weight[0]
        remark_width = weight[1]
        in_width = weight[2]
        out_width = weight[3]
        group_width = max(group_width, 60)
        if remark_width < 60:
            remark_width = 90
        in_width = max(in_width, 180)
        out_width = max(out_width, 180)
        other_width = 100

        abema_logo = Image.open(f"{LOGOS_DIR}Abema.png")
        abema_logo.thumbnail((28, 28))
        bahamut_logo = Image.open(f"{LOGOS_DIR}Bahamut.png")
        bahamut_logo.thumbnail((28, 28))
        bilibili_logo = Image.open(f"{LOGOS_DIR}Bilibili.png")
        bilibili_logo.thumbnail((28, 28))
        dazn_logo = Image.open(f"{LOGOS_DIR}Dazn.png")
        dazn_logo.thumbnail((28, 28))
        disney_logo = Image.open(f"{LOGOS_DIR}DisneyPlus.png")
        disney_logo.thumbnail((28, 28))
        hbo_logo = Image.open(f"{LOGOS_DIR}HBO.png")
        hbo_logo.thumbnail((28, 28))
        netflix_logo = Image.open(f"{LOGOS_DIR}Netflix.png")
        netflix_logo.thumbnail((28, 28))
        tvb_logo = Image.open(f"{LOGOS_DIR}TVB.png")
        tvb_logo.thumbnail((28, 28))
        youtube_logo = Image.open(f"{LOGOS_DIR}YouTube.png")
        youtube_logo.thumbnail((28, 28))

        group_right_position = group_width
        remark_right_position = group_right_position + remark_width
        image_right_position = remark_right_position

        if not self.__hide_gping:
            image_right_position = remark_right_position + other_width
        loss_right_position = image_right_position

        if not self.__hide_ping:
            image_right_position = loss_right_position + other_width
        tcp_ping_right_position = image_right_position

        if not self.__hide_gping:
            image_right_position = tcp_ping_right_position + other_width + 25
        google_ping_right_position = image_right_position

        if not self.__hide_port:
            image_right_position = google_ping_right_position + other_width
        port_right_position = image_right_position

        if not self.__hide_speed:
            image_right_position = port_right_position + other_width
        dspeed_right_position = image_right_position

        if not (self.__hide_max_speed or self.__hide_speed):
            image_right_position = dspeed_right_position + other_width
        max_dspeed_right_position = image_right_position

        if not self.__hide_ntt:
            image_right_position = image_right_position + other_width + 80
        ntt_right_position = image_right_position

        if not self.__hide_netflix:
            image_right_position = image_right_position + other_width + 60
        netflix_right_position = image_right_position

        if not self.__hide_bilibili:
            image_right_position = image_right_position + other_width + 60
        bilibili_right_position = image_right_position

        if not self.__hide_stream:
            image_right_position = image_right_position + other_width + 200
        stream_right_position = image_right_position

        if not self.__hide_geoip:
            image_right_position = image_right_position + in_width
        inbound_right_position = image_right_position

        if not self.__hide_geoip:
            image_right_position = image_right_position + out_width
        outbound_right_position = image_right_position

        if not self.__hide_multiplex:
            image_right_position = image_right_position + other_width + 10
        multiplex_right_position = image_right_position

        new_image_height = image_height + 30 * 3
        result_img = Image.new(
            "RGB", (image_right_position, new_image_height), (255, 255, 255)
        )
        draw = ImageDraw.Draw(result_img)
        pilmoji = Pilmoji(result_img, emoji_position_offset=(0, 3))

        # draw.line(
        #     (
        #         0,
        #         new_image_height - 30 - 1,
        #         image_right_position,
        #         new_image_height - 30 - 1,
        #     ),
        #     fill=(127, 127, 127),
        #     width=1,
        # )

        try:
            text = f'\u2708\uFE0F 机场测评图 with SSRSpeed N ( v{ssrconfig["VERSION"]} )'
            pilmoji.text(
                (int(self.__get_base_pos(image_right_position, text)), 4),
                text,
                font=result_font,
                fill=(0, 0, 0),
            )
        except Exception:
            text = f'机场测评图 with SSRSpeed N ( v{ssrconfig["VERSION"]} )'
            draw.text(
                (self.__get_base_pos(image_right_position, text), 4),
                text,
                font=result_font,
                fill=(0, 0, 0),
            )
        draw.line((0, 30, image_right_position - 1, 30), fill=(127, 127, 127), width=1)

        draw.line((1, 0, 1, new_image_height - 1), fill=(127, 127, 127), width=1)
        draw.line(
            (group_right_position, 30, group_right_position, image_height + 30 - 1),
            fill=(127, 127, 127),
            width=1,
        )
        draw.line(
            (remark_right_position, 30, remark_right_position, image_height + 30 - 1),
            fill=(127, 127, 127),
            width=1,
        )

        if not self.__hide_gping:
            draw.line(
                (loss_right_position, 30, loss_right_position, image_height + 30 - 1),
                fill=(127, 127, 127),
                width=1,
            )

        if not self.__hide_ping:
            draw.line(
                (
                    tcp_ping_right_position,
                    30,
                    tcp_ping_right_position,
                    image_height + 30 - 1,
                ),
                fill=(127, 127, 127),
                width=1,
            )

        if not self.__hide_gping:
            draw.line(
                (
                    google_ping_right_position,
                    30,
                    google_ping_right_position,
                    image_height + 30 - 1,
                ),
                fill=(127, 127, 127),
                width=1,
            )

        if not self.__hide_port:
            draw.line(
                (port_right_position, 30, port_right_position, image_height + 30 - 1),
                fill=(127, 127, 127),
                width=1,
            )

        if not self.__hide_speed:
            draw.line(
                (
                    dspeed_right_position,
                    30,
                    dspeed_right_position,
                    image_height + 30 - 1,
                ),
                fill=(127, 127, 127),
                width=1,
            )
            if not self.__hide_max_speed:
                draw.line(
                    (
                        max_dspeed_right_position,
                        30,
                        max_dspeed_right_position,
                        image_height + 30 - 1,
                    ),
                    fill=(127, 127, 127),
                    width=1,
                )

        if not self.__hide_ntt:
            draw.line(
                (ntt_right_position, 30, ntt_right_position, image_height + 30 - 1),
                fill=(127, 127, 127),
                width=1,
            )

        if not self.__hide_netflix:
            draw.line(
                (
                    netflix_right_position,
                    30,
                    netflix_right_position,
                    image_height + 30 - 1,
                ),
                fill=(127, 127, 127),
                width=1,
            )

        if not self.__hide_bilibili:
            draw.line(
                (
                    bilibili_right_position,
                    30,
                    bilibili_right_position,
                    image_height + 30 - 1,
                ),
                fill=(127, 127, 127),
                width=1,
            )

        if not self.__hide_stream:
            draw.line(
                (
                    stream_right_position,
                    30,
                    stream_right_position,
                    image_height + 30 - 1,
                ),
                fill=(127, 127, 127),
                width=1,
            )

        if not self.__hide_geoip:
            draw.line(
                (
                    inbound_right_position,
                    30,
                    inbound_right_position,
                    image_height + 30 - 1,
                ),
                fill=(127, 127, 127),
                width=1,
            )

        if not self.__hide_geoip:
            draw.line(
                (
                    outbound_right_position,
                    30,
                    outbound_right_position,
                    image_height + 30 - 1,
                ),
                fill=(127, 127, 127),
                width=1,
            )

        if not self.__hide_multiplex:
            draw.line(
                (
                    multiplex_right_position,
                    30,
                    multiplex_right_position,
                    image_height + 30 - 1,
                ),
                fill=(127, 127, 127),
                width=1,
            )

        draw.line(
            (image_right_position, 0, image_right_position, new_image_height - 1),
            fill=(127, 127, 127),
            width=1,
        )

        draw.line((0, 0, image_right_position - 1, 0), fill=(127, 127, 127), width=1)

        draw.text(
            (self.__get_base_pos(group_right_position, "Group"), 30 + 4),
            "Group",
            font=result_font,
            fill=(0, 0, 0),
        )

        draw.text(
            (
                group_right_position
                + self.__get_base_pos(
                    remark_right_position - group_right_position, "Remarks"
                ),
                30 + 4,
            ),
            "Remarks",
            font=result_font,
            fill=(0, 0, 0),
        )

        if not self.__hide_gping:
            draw.text(
                (
                    remark_right_position
                    + self.__get_base_pos(
                        loss_right_position - remark_right_position, "Loss"
                    ),
                    30 + 4,
                ),
                "Loss",
                font=result_font,
                fill=(0, 0, 0),
            )

        if not self.__hide_ping:
            draw.text(
                (
                    loss_right_position
                    + self.__get_base_pos(
                        tcp_ping_right_position - loss_right_position, "Ping"
                    ),
                    30 + 4,
                ),
                "Ping",
                font=result_font,
                fill=(0, 0, 0),
            )

        if not self.__hide_gping:
            draw.text(
                (
                    tcp_ping_right_position
                    + self.__get_base_pos(
                        google_ping_right_position - tcp_ping_right_position,
                        "Google Ping",
                    ),
                    30 + 4,
                ),
                "Google Ping",
                font=result_font,
                fill=(0, 0, 0),
            )

        if not self.__hide_port:
            draw.text(
                (
                    google_ping_right_position
                    + self.__get_base_pos(
                        port_right_position - google_ping_right_position, "Port"
                    ),
                    30 + 4,
                ),
                "Port",
                font=result_font,
                fill=(0, 0, 0),
            )

        if not (self.__hide_stspeed or self.__hide_speed):
            if self.__test_method == "NETFLIX":
                draw.text(
                    (
                        port_right_position
                        + self.__get_base_pos(
                            dspeed_right_position - port_right_position, "EndSpeed"
                        ),
                        30 + 4,
                    ),
                    "EndSpeed",
                    font=result_font,
                    fill=(0, 0, 0),
                )
            elif self.__test_method == "YOUTUBE":
                draw.text(
                    (
                        port_right_position
                        + self.__get_base_pos(
                            dspeed_right_position - port_right_position, "StSpeed"
                        ),
                        30 + 4,
                    ),
                    "StSpeed",
                    font=result_font,
                    fill=(0, 0, 0),
                )
            else:
                draw.text(
                    (
                        port_right_position
                        + self.__get_base_pos(
                            dspeed_right_position - port_right_position, "单线程"
                        ),
                        30 + 4,
                    ),
                    "单线程",
                    font=result_font,
                    fill=(0, 0, 0),
                )
        elif not self.__hide_speed:
            if self.__test_method == "NETFLIX":
                draw.text(
                    (
                        port_right_position
                        + self.__get_base_pos(
                            dspeed_right_position - port_right_position, "EndSpeed"
                        ),
                        30 + 4,
                    ),
                    "EndSpeed",
                    font=result_font,
                    fill=(0, 0, 0),
                )
            elif self.__test_method == "YOUTUBE":
                draw.text(
                    (
                        port_right_position
                        + self.__get_base_pos(
                            dspeed_right_position - port_right_position, "StSpeed"
                        ),
                        30 + 4,
                    ),
                    "StSpeed",
                    font=result_font,
                    fill=(0, 0, 0),
                )
            else:
                draw.text(
                    (
                        port_right_position
                        + self.__get_base_pos(
                            dspeed_right_position - port_right_position, "AvgSpeed"
                        ),
                        30 + 4,
                    ),
                    "AvgSpeed",
                    font=result_font,
                    fill=(0, 0, 0),
                )

        if not (self.__hide_max_speed or self.__hide_speed):
            if not self.__hide_stspeed:
                draw.text(
                    (
                        dspeed_right_position
                        + self.__get_base_pos(
                            max_dspeed_right_position - dspeed_right_position, "多线程"
                        ),
                        30 + 4,
                    ),
                    "多线程",
                    font=result_font,
                    fill=(0, 0, 0),
                )
            else:
                draw.text(
                    (
                        dspeed_right_position
                        + self.__get_base_pos(
                            max_dspeed_right_position - dspeed_right_position,
                            "MaxSpeed",
                        ),
                        30 + 4,
                    ),
                    "MaxSpeed",
                    font=result_font,
                    fill=(0, 0, 0),
                )

        if not self.__hide_ntt:
            draw.text(
                (
                    max_dspeed_right_position
                    + self.__get_base_pos(
                        ntt_right_position - max_dspeed_right_position, "UDP NAT Type"
                    ),
                    30 + 4,
                ),
                "UDP NAT Type",
                font=result_font,
                fill=(0, 0, 0),
            )

        if not self.__hide_netflix:
            draw.text(
                (
                    ntt_right_position
                    + self.__get_base_pos(
                        netflix_right_position - ntt_right_position, "Netfilx 解锁"
                    ),
                    30 + 4,
                ),
                "Netfilx 解锁",
                font=result_font,
                fill=(0, 0, 0),
            )

        if not self.__hide_bilibili:
            draw.text(
                (
                    netflix_right_position
                    + self.__get_base_pos(
                        bilibili_right_position - netflix_right_position, "Netfilx 解锁"
                    ),
                    30 + 4,
                ),
                "Bilibili 解锁",
                font=result_font,
                fill=(0, 0, 0),
            )

        if not self.__hide_stream:
            draw.text(
                (
                    bilibili_right_position
                    + self.__get_base_pos(
                        stream_right_position - bilibili_right_position, "流媒体解锁"
                    ),
                    30 + 4,
                ),
                "流媒体解锁",
                font=result_font,
                fill=(0, 0, 0),
            )
        draw.line((0, 60, image_right_position - 1, 60), fill=(127, 127, 127), width=1)

        if not self.__hide_geoip:
            draw.text(
                (
                    stream_right_position
                    + self.__get_base_pos(
                        inbound_right_position - stream_right_position, "Inbound Geo"
                    ),
                    30 + 4,
                ),
                "Inbound Geo",
                font=result_font,
                fill=(0, 0, 0),
            )

        if not self.__hide_geoip:
            draw.text(
                (
                    inbound_right_position
                    + self.__get_base_pos(
                        outbound_right_position - inbound_right_position, "Outbound Geo"
                    ),
                    30 + 4,
                ),
                "Outbound Geo",
                font=result_font,
                fill=(0, 0, 0),
            )

        if not self.__hide_multiplex:
            draw.text(
                (
                    outbound_right_position
                    + self.__get_base_pos(
                        multiplex_right_position - outbound_right_position, "复用检测"
                    ),
                    30 + 4,
                ),
                "复用检测",
                font=result_font,
                fill=(0, 0, 0),
            )

        total_traffic = 0
        online_node = 0
        for i, r in enumerate(result):
            total_traffic += r["trafficUsed"] if (r["trafficUsed"] > 0) else 0
            if (r["ping"] > 0 and r["gPing"] > 0) or (r["dspeed"] > 0):
                online_node += 1

            j = i + 1
            draw.line(
                (0, 30 * j + 60, image_right_position, 30 * j + 60),
                fill=(127, 127, 127),
                width=1,
            )

            group = r["group"]
            remarks = r["remarks"]
            try:
                pilmoji.text(
                    (5, 30 * j + 30 + 4), group, font=result_font, fill=(0, 0, 0)
                )
                pilmoji.text(
                    (group_right_position + 5, 30 * j + 30 + 4),
                    remarks,
                    font=result_font,
                    fill=(0, 0, 0, 0),
                )
            except Exception:
                draw.text((5, 30 * j + 30 + 4), group, font=result_font, fill=(0, 0, 0))
                draw.text(
                    (group_right_position + 5, 30 * j + 30 + 4),
                    remarks,
                    font=result_font,
                    fill=(0, 0, 0, 0),
                )

            if not self.__hide_gping:
                loss = f'{r["gPingLoss"] * 100:.2f}%'
                pos = remark_right_position + self.__get_base_pos(
                    loss_right_position - remark_right_position, loss
                )
                draw.text(
                    (pos, 30 * j + 30 + 4), loss, font=result_font, fill=(0, 0, 0)
                )

            if not self.__hide_ping:
                ping = f'{r["ping"] * 1000:.2f}'
                pos = loss_right_position + self.__get_base_pos(
                    tcp_ping_right_position - loss_right_position, ping
                )
                draw.text(
                    (pos, 30 * j + 30 + 4), ping, font=result_font, fill=(0, 0, 0)
                )

            if not self.__hide_gping:
                g_ping = f'{r["gPing"] * 1000:.2f}'
                pos = tcp_ping_right_position + self.__get_base_pos(
                    google_ping_right_position - tcp_ping_right_position, g_ping
                )
                draw.text(
                    (pos, 30 * j + 30 + 4), g_ping, font=result_font, fill=(0, 0, 0)
                )

            if not self.__hide_port:
                port = str(r["port"])
                pos = google_ping_right_position + self.__get_base_pos(
                    port_right_position - google_ping_right_position, port
                )
                draw.text(
                    (pos, 30 * j + 30 + 4), port, font=result_font, fill=(0, 0, 0)
                )

            if not self.__hide_speed:
                speed = r["dspeed"]
                if speed == -1:
                    pos = port_right_position + self.__get_base_pos(
                        dspeed_right_position - port_right_position, "N/A"
                    )
                    draw.text(
                        (pos, 30 * j + 30 + 1), "N/A", font=result_font, fill=(0, 0, 0)
                    )
                else:
                    draw.rectangle(
                        (
                            port_right_position + 1,
                            30 * j + 30 + 1,
                            dspeed_right_position - 1,
                            30 * j + 60 - 1,
                        ),
                        self.__get_color(speed),
                    )
                    speed = self.__parse_speed(speed)
                    pos = port_right_position + self.__get_base_pos(
                        dspeed_right_position - port_right_position, speed
                    )
                    draw.text(
                        (pos, 30 * j + 30 + 1), speed, font=result_font, fill=(0, 0, 0)
                    )

            if not (self.__hide_max_speed or self.__hide_speed):
                max_speed = r["maxDSpeed"]
                if max_speed == -1:
                    pos = dspeed_right_position + self.__get_base_pos(
                        max_dspeed_right_position - dspeed_right_position, "N/A"
                    )
                    draw.text(
                        (pos, 30 * j + 30 + 1), "N/A", font=result_font, fill=(0, 0, 0)
                    )
                else:
                    draw.rectangle(
                        (
                            dspeed_right_position + 1,
                            30 * j + 30 + 1,
                            max_dspeed_right_position - 1,
                            30 * j + 60 - 1,
                        ),
                        self.__get_color(max_speed),
                    )
                    max_speed = self.__parse_speed(max_speed)
                    pos = dspeed_right_position + self.__get_base_pos(
                        max_dspeed_right_position - dspeed_right_position, max_speed
                    )
                    draw.text(
                        (pos, 30 * j + 30 + 1),
                        max_speed,
                        font=result_font,
                        fill=(0, 0, 0),
                    )

            if not self.__hide_ntt:
                nat_type = r["ntt"]["type"]
                if not nat_type:
                    pos = max_dspeed_right_position + self.__get_base_pos(
                        ntt_right_position - max_dspeed_right_position, "Unknown"
                    )
                    draw.text(
                        (pos, 30 * j + 30 + 1),
                        "Unknown",
                        font=result_font,
                        fill=(0, 0, 0),
                    )
                else:
                    pos = max_dspeed_right_position + self.__get_base_pos(
                        ntt_right_position - max_dspeed_right_position, nat_type
                    )
                    draw.text(
                        (pos, 30 * j + 30 + 1),
                        nat_type,
                        font=result_font,
                        fill=(0, 0, 0),
                    )

            if not self.__hide_netflix:
                netflix_type = r["Ntype"]
                pos = ntt_right_position + self.__get_base_pos(
                    netflix_right_position - ntt_right_position, netflix_type
                )
                draw.text(
                    (pos, 30 * j + 30 + 1),
                    netflix_type,
                    font=result_font,
                    fill=(0, 0, 0),
                )

            if not self.__hide_bilibili:
                bilibili_type = r["Bltype"]
                pos = netflix_right_position + self.__get_base_pos(
                    bilibili_right_position - netflix_right_position, bilibili_type
                )
                draw.text(
                    (pos, 30 * j + 30 + 1),
                    bilibili_type,
                    font=result_font,
                    fill=(0, 0, 0),
                )

            if not self.__hide_stream:
                netflix_type = r["Ntype"]
                hbo_type = r["Htype"]
                disney_type = r["Dtype"]
                youtube_type = r["Ytype"]
                abema_type = r["Atype"]
                bahamut_type = r["Btype"]
                dazn_type = r["Dztype"]
                tvb_type = r["Ttype"]
                bilibili_type = r["Bltype"]
                n_type = bool(netflix_type[:4] == "Full")
                bl_type = bool(bilibili_type != "N/A")
                sums = (
                    n_type
                    + hbo_type
                    + disney_type
                    + youtube_type
                    + abema_type
                    + bahamut_type
                    + dazn_type
                    + bl_type
                    + tvb_type
                )
                pos = (
                    bilibili_right_position
                    + (stream_right_position - bilibili_right_position - sums * 35) / 2
                )
                if n_type:
                    result_img.paste(netflix_logo, (int(pos), 30 * j + 30 + 1))
                    pos += 35
                if hbo_type:
                    result_img.paste(hbo_logo, (int(pos), 30 * j + 30 + 1))
                    pos += 35
                if disney_type:
                    result_img.paste(disney_logo, (int(pos), 30 * j + 30 + 1))
                    pos += 35
                if youtube_type:
                    result_img.paste(youtube_logo, (int(pos), 30 * j + 30 + 1))
                    pos += 35
                if abema_type:
                    result_img.paste(abema_logo, (int(pos), 30 * j + 30 + 1))
                    pos += 35
                if bahamut_type:
                    result_img.paste(bahamut_logo, (int(pos), 30 * j + 30 + 1))
                    pos += 35
                if dazn_type:
                    result_img.paste(dazn_logo, (int(pos), 30 * j + 30 + 1))
                    pos += 35
                if tvb_type:
                    result_img.paste(tvb_logo, (int(pos), 30 * j + 30 + 1))
                    pos += 35
                if bl_type:
                    result_img.paste(bilibili_logo, (int(pos), 30 * j + 30 + 1))
                    pos += 35

            if not self.__hide_geoip:
                inbound_geo = r["InRes"]
                pos = stream_right_position + self.__get_base_pos(
                    inbound_right_position - stream_right_position, inbound_geo
                )
                draw.text(
                    (pos, 30 * j + 30 + 1),
                    inbound_geo,
                    font=result_font,
                    fill=(0, 0, 0),
                )

            if not self.__hide_geoip:
                outbound_geo = r["OutRes"]
                pos = inbound_right_position + self.__get_base_pos(
                    outbound_right_position - inbound_right_position, outbound_geo
                )
                draw.text(
                    (pos, 30 * j + 30 + 1),
                    outbound_geo,
                    font=result_font,
                    fill=(0, 0, 0),
                )

            if not self.__hide_geoip:
                inbound_ip = r["InIP"]
                outbound_ip = r["OutIP"]
                multiplex_res = ""
                if outbound_ip != "N/A":
                    inbound_mul = -1
                    outbound_mul = -1
                    if inbound_ip == "N/A":
                        inbound_mul = 0
                    for _, ipitem in enumerate(result):
                        if ipitem["InIP"] == inbound_ip and inbound_ip != "N/A":
                            inbound_mul += 1
                        if ipitem["OutIP"] == outbound_ip:
                            outbound_mul += 1
                    if inbound_mul and outbound_mul:
                        multiplex_res = "完全复用"
                    elif (not inbound_mul) and (not outbound_mul):
                        multiplex_res = "无复用"
                    elif inbound_mul:
                        multiplex_res = "中转复用"
                    elif outbound_mul:
                        multiplex_res = "落地复用"
                else:
                    multiplex_res = "未知"

                pos = outbound_right_position + self.__get_base_pos(
                    multiplex_right_position - outbound_right_position, multiplex_res
                )
                draw.text(
                    (pos, 30 * j + 30 + 1),
                    multiplex_res,
                    font=result_font,
                    fill=(0, 0, 0),
                )

        files = []
        if total_traffic < 0:
            traffic_used = "N/A"
        else:
            traffic_used = self.__parse_traffic(total_traffic)

        if not self.__hide_speed:
            t1 = f"Traffic used : {traffic_used}. "
        else:
            t1 = ""

        if not self.__hide_gping:
            t2 = f" Online Node(s) : [{online_node}/{len(result)}]"
        else:
            t2 = ""

        with open(TEST_TXT, "a+", encoding="utf-8") as test:
            test.seek(0)
            url = test.readline()
            try:
                sum0 = int(test.readline())
            except ValueError:
                sum0 = 0
        os.remove(TEST_TXT)

        if not self.__hide_speed:
            clash_ua = {"User-Agent": "Clash"}

            try:
                r = requests.get(url, headers=clash_ua, timeout=15)
                t = r.headers["subscription-userinfo"]
                dl = int(t[t.find("download") + 9 : t.find("total") - 2])
                sum_ = dl
            except Exception:
                sum_ = 0
            avgrate = (sum_ - sum0) / total_traffic if total_traffic else 0
            if (sum_ - sum0) > 0:
                t3 = f".  AvgRate : {avgrate:.2f}"
            else:
                t3 = ""
        else:
            t3 = ""

        draw.text(
            (5, image_height + 30 + 4),
            t1 + f"Time used: {self.__time_used}." + t2 + t3,
            font=result_font,
            fill=(0, 0, 0),
        )

        # draw.line(
        #     (
        #         0,
        #         new_image_height - 30 * 3 - 1,
        #         image_right_position,
        #         new_image_height - 30 * 3 - 1,
        #     ),
        #     fill=(127, 127, 127),
        #     width=1,
        # )

        draw.text(
            (5, image_height + 30 * 2 + 4),
            f'{self.__addition}  Generated at {time.strftime("%Y-%m-%d %H:%M:%S", generated_time)}',
            font=result_font,
            fill=(0, 0, 0),
        )
        draw.line(
            (
                0,
                new_image_height - 30 - 1,
                image_right_position,
                new_image_height - 30 - 1,
            ),
            fill=(127, 127, 127),
            width=1,
        )

        # draw.line(
        #     (
        #         0,
        #         new_image_height - 30 - 1,
        #         image_right_position,
        #         new_image_height - 30 - 1,
        #     ),
        #     fill=(127, 127, 127),
        #     width=1,
        # )
        # draw.text(
        #     (5, image_height + 30 * 2 + 4),
        #     f'By SSRSpeed {ssrconfig["VERSION"]}.',
        #     font=result_font,
        #     fill=(0, 0, 0),
        # )

        draw.line(
            (0, new_image_height - 1, image_right_position, new_image_height - 1),
            fill=(127, 127, 127),
            width=1,
        )
        filename = (
            RESULTS_DIR + time.strftime("%Y-%m-%d-%H-%M-%S", generated_time) + ".png"
        )
        result_img.save(filename)
        files.append(filename)
        logger.info(f"Result image saved as {filename}")

        if not self.__config.get("uploadResult", False):
            self.__upload_result(files)

    def __upload_result(self, files: list):
        sever = self.__upload_config.get("server", "")
        token = self.__upload_config.get("token", "")
        remark = self.__upload_config.get("remark", "")
        for _file in files:
            push2server(_file, sever, token, remark)

    @staticmethod
    def __parse_traffic(traffic: float) -> str:
        traffic = traffic / 1024 / 1024
        if traffic < 1:
            return f"{traffic * 1024:.2f} KB"
        gb_traffic = traffic / 1024
        return f"{traffic:.2f} MB" if gb_traffic < 1 else f"{gb_traffic:.2f} GB"

    @staticmethod
    def __parse_speed(speed: float) -> str:
        speed = speed / 1024 / 1024
        return f"{speed * 1024:.2f} KB" if speed < 1 else f"{speed:.2f} MB"

    @staticmethod
    def __new_mix_color(lc: dict, rc: dict, rt: int) -> tuple:
        #   print("RGB1 : {lc}, RGB2 : {rc}, RT : {rt}")
        return (
            int(lc[0] * (1 - rt) + rc[0] * rt),
            int(lc[1] * (1 - rt) + rc[1] * rt),
            int(lc[2] * (1 - rt) + rc[2] * rt),
        )

    def __get_color(self, data: float) -> tuple:
        if not self.__color_speed_list:
            return 255, 255, 255
        cur_speed = self.__color_speed_list[-1]
        back_speed = 0
        if data >= cur_speed * 1024 * 1024:
            return (
                self.__colors[str(cur_speed)][0],
                self.__colors[str(cur_speed)][1],
                self.__colors[str(cur_speed)][2],
            )
        for i, s in enumerate(self.__color_speed_list):
            cur_speed = s * 1024 * 1024
            if i > 0:
                back_speed = self.__color_speed_list[i - 1]
            back_speed_str = str(back_speed)
            #   print(f"{data / 1024 / 1024} {back_speed}")
            if data < cur_speed:
                rgb1 = (
                    self.__colors[back_speed_str] if back_speed > 0 else (255, 255, 255)
                )
                rgb2 = self.__colors[str(s)]
                rt = (data - back_speed * 1024 * 1024) / (
                    cur_speed - back_speed * 1024 * 1024
                )
                logger.debug(
                    f"Speed : {data / 1024 / 1024}, RGB1 : {rgb1}, RGB2 : {rgb2}, RT : {rt}"
                )
                return self.__new_mix_color(rgb1, rgb2, rt)
        return 255, 255, 255

    @staticmethod
    def __export_as_json(result: list) -> list:
        filename = (
            RESULTS_DIR + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".json"
        )
        with open(filename, "w+", encoding="utf-8") as f:
            f.writelines(
                json.dumps(result, sort_keys=True, indent=4, separators=(",", ":"))
            )
        logger.info(f"Result exported as {filename}")
        return result
