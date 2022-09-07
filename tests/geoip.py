import geoip2.database
from geoip2.errors import AddressNotFoundError

from tests import root

root()


def geo_info(ip):
    country, country_code, city, organization = "N/A", "N/A", "Unknown City", "N/A"
    try:
        # This creates a Reader object. You should use the same object
        # across multiple requests as creation of it is expensive.
        with geoip2.database.Reader("data/database/GeoLite2-City.mmdb") as reader:

            # Replace "city" with the method corresponding to the database
            # that you are using, e.g., "country".
            # response = reader.city(ip)
            # print(response)

            country_info = reader.city(ip).country
            country = country_info.names.get("en", "N/A")
            country_code = country_info.iso_code
            city = reader.city(ip).city.names.get("en", "Unknown City")
            # print(country, country_code, city)

    except ValueError as e:
        print(e)

    try:
        with geoip2.database.Reader("data/database/GeoLite2-ASN.mmdb") as reader:

            # response = reader.asn(ip)
            # print(response)

            organization = reader.asn(ip).autonomous_system_organization
            # print(organization)

    except AddressNotFoundError as e:
        print(e)

    return country, country_code, city, organization


if __name__ == "__main__":
    print(geo_info("97.10.26.3"))
    print(geo_info("198.23.17.4"))
    print(geo_info("25.8.96.5"))
    print(geo_info("36.172.109.83"))
    print(geo_info("125.34.39.7"))
    print(geo_info("181.37.231.90"))
