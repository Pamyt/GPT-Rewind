"""iso time utils"""
from dateutil import parser

def delta_to_dhms(iso_str1, iso_str2):
    """extract days, hours, minutes, seconds from two iso time strings"""
    dt1 = parser.isoparse(iso_str1)
    dt2 = parser.isoparse(iso_str2)

    # 确保 dt2 >= dt1；如果不确定顺序，可取绝对值
    delta = dt2 - dt1 if dt2 >= dt1 else dt1 - dt2

    total_seconds = int(delta.total_seconds())

    days = total_seconds // (24 * 3600)
    remainder = total_seconds % (24 * 3600)

    hours = remainder // 3600
    remainder %= 3600

    minutes = remainder // 60
    seconds = remainder % 60

    return days, hours, minutes, seconds, total_seconds

def extract_time(iso_str):
    """extract HH:MM:SS from iso time string"""
    datetime_obj = parser.isoparse(iso_str)
    return f"{datetime_obj.hour:02}:{datetime_obj.minute:02}:{datetime_obj.second:02}"

def main():
    """main function to test"""
    # 示例
    iso_time1 = "2024-12-04T14:51:13.146000+08:00"
    iso_time2 = "2024-12-06T18:25:30.000000+08:00"

    days, hours, minutes, seconds, _ = delta_to_dhms(iso_time1, iso_time2)
    print(f"{days}d {hours}h {minutes}m {seconds}s")

if __name__ == "__main__":
    main()
