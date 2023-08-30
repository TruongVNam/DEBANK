import os
from datetime import datetime
import json
import pandas as pd
import time
import pytz
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def sleep_milliseconds(milliseconds):
    seconds = milliseconds / 1000.0
    time.sleep(seconds)


def format_datetime(dt):
    return dt.strftime("%Y-%m-%d")


def format_date(date_str):
    current_year = datetime.now().year

    date_formats = [
        "%m/%d/%Y",
        "%m %d %Y",
        "%d/%m/%Y",
        "%d %m %Y",
        "%b/%d/%Y",
        "%b %d %Y",
        "%d/%b/%Y",
        "%d %b %Y",
        "%d %b",
    ]

    new_date_str = None

    for date_format in date_formats:
        try:
            date_obj = datetime.strptime(date_str, date_format)
            new_date_str = date_obj.strftime("%d-%m-%Y")
            break
        except ValueError:
            continue

    if not new_date_str:
        return None

    if new_date_str.count("-") < 2:
        new_date_str = f"{new_date_str}-{current_year}"

    return new_date_str


def print_current_datetime():
    now = datetime.now()
    formatted_date = now.strftime("%d-%m-%Y")
    formatted_time = now.strftime("%H:%M:%S")
    # print(f"Ngày: {formatted_date}, Giờ: {formatted_time}")
    return formatted_date + " " + formatted_time


def is_first_monday_of_month():
    today = datetime.today()
    if today.weekday() == 0 and today.day <= 7:
        return True
    else:
        return False


def is_monday_utc():
    utc_now = datetime.now(pytz.utc)
    return utc_now.weekday()


def format_file_json(input_file):
    current_time = datetime.now(pytz.utc)
    formatted_time = format_datetime(current_time)
    output_file = {"time": formatted_time, "data": input_file}

    return output_file


def read_write_file_json(
    file_name, action, data_to_convert_json=None, directory_path=None
):
    default_dir = "D:\Code\DEBANK"
    data_dir = directory_path if directory_path else os.path.join(default_dir, "data")
    dest_path = os.path.join(data_dir, file_name)

    try:
        if action == "r":
            with open(dest_path, "r") as json_data:  # Thêm mode "r" khi đọc tệp JSON
                return json.load(json_data)
        elif action == "w":
            with open(dest_path, "w") as file:  # Thêm mode "w" khi ghi tệp JSON
                json.dump(data_to_convert_json, file)
        else:
            raise ValueError(
                "Invalid action. Please use 'r' for reading or 'w' for writing."
            )

        if action == "r":
            print("Reading file successfully")
        elif action == "w":
            print("Writing file successfully")

    except FileNotFoundError:
        os.makedirs(data_dir, exist_ok=True)
        if action == "w":
            with open(dest_path, "w") as file:  # Thêm mode "w" khi tạo tệp JSON mới
                json.dump(data_to_convert_json, file)
        raise ValueError("Could not find the 'data' directory.")


def transform_and_save_json_file(
    destination_dir=None,
    file_name=None,
    action=None,
    data_to_convert_json=None,
    data_dir=None,
):
    default_dir = "D:\Code\DEBANK"
    if data_dir is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir_candidates = [current_dir, os.path.dirname(current_dir)]
        for candidate in data_dir_candidates:
            data_candidate = os.path.join(candidate, "data")
            if os.path.exists(data_candidate) and os.path.isdir(data_candidate):
                data_dir = data_candidate
                break
        if data_dir is None:
            data_dir = os.path.join(default_dir, "data")
            if os.path.exists(data_dir):
                pass
            else:
                os.makedirs(data_dir)

    if destination_dir is None:
        destination_dir = "D:\DBCDA"

    current_time = datetime.now(pytz.utc)
    formatted_time = current_time.strftime("%Y%m%d")

    if file_name is None:
        file_name = formatted_time + ".json"

    dest_path = os.path.join(data_dir, file_name)

    # Check if the destination directory exists, create if not
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Check if the subdirectory with current date exists
    subdirectory = os.path.join(destination_dir, formatted_time)
    if not os.path.exists(subdirectory):
        os.makedirs(subdirectory)

    dest_file_path = os.path.join(subdirectory, file_name)

    try:
        read_write_file_json(dest_path, action, data_to_convert_json)
        print(f"Successfully transformed and saved data as '{file_name}'.")

        read_write_file_json(dest_file_path, action, data_to_convert_json)
        print(
            f"Successfully transformed and saved data as '{file_name}' to '{subdirectory}'."
        )

    except Exception as e:
        print(f"An error occurred while transforming and saving the data: {str(e)}")


def create_driver():
    service = Service("C:\Drivers\chromedriver-win64\chromedriver.exe")
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def go_to_web_url(driver, url):
    driver.get(url)
    print(f"Go to website: {url}")


def get_active_xpath(driver, elements_xpath_tree):
    ancestor_elements_xpath = elements_xpath_tree["ancestor_elements_xpath"]
    parent_elements_xpath = elements_xpath_tree["parent_elements_xpath"]
    descendant_elements_xpath = elements_xpath_tree["descendant_elements_xpath"]
    # driver.implicitly_wait(10)

    for ancestor_element in ancestor_elements_xpath:
        for parent_element in parent_elements_xpath:
            for descendant_element in descendant_elements_xpath:
                element_xpath_combine = (
                    ancestor_element + parent_element + descendant_element
                )
                try:
                    driver.find_element(By.XPATH, element_xpath_combine)
                    return element_xpath_combine
                except NoSuchElementException:
                    continue

    return None


def get_last_page(driver, last_page_path=None):
    if last_page_path is None:
        last_page_path = "//ul/li[8]"

    try:
        last_page_index = driver.find_element(By.XPATH, last_page_path).text
        last_page = int(last_page_index)
        is_only_one_page = False
        print(f"The table last page is: {last_page}")
    except NoSuchElementException:
        print(
            "There is only one Page, therefore can't find the page button to navigate to a new page"
        )
        is_only_one_page = True
        last_page = 1

    return [is_only_one_page, last_page]


def is_element_in_viewport(driver, element_xpath):
    # print(f'The element xpath: {element_xpath}')
    element = driver.find_element(By.XPATH, element_xpath)
    viewport_height = driver.execute_script("return window.innerHeight;")
    viewport_top = driver.execute_script("return window.pageYOffset;")
    viewport_bottom = viewport_top + viewport_height

    element_top = driver.execute_script(
        "return arguments[0].getBoundingClientRect().top;", element
    )
    element_bottom = driver.execute_script(
        "return arguments[0].getBoundingClientRect().bottom;", element
    )

    if element_top >= viewport_top and element_bottom <= viewport_bottom:
        return True
    else:
        return False


def click_element_by_script(driver, click_elements_xpath):
    click_element_script = """
        var element = arguments[0];
        element.click();
    """
    if isinstance(click_elements_xpath, dict):
        ancestor_elements_xpath = click_elements_xpath["ancestor_elements_xpath"]
        parent_elements_xpath = click_elements_xpath["parent_elements_xpath"]
        children_element_xpath = click_elements_xpath["children_element_xpath"]

        found_element = False
        for ancestor_element in ancestor_elements_xpath:
            try:
                for parent_element in parent_elements_xpath:
                    check_element = ancestor_element + parent_element
                    elements = driver.find_elements(
                        By.XPATH, check_element + children_element_xpath
                    )
                    for element in elements:
                        driver.execute_script(click_element_script, element)
                        found_element = True
                        break
                    if found_element:
                        break
            except NoSuchElementException:
                continue
            else:
                break
    elif isinstance(click_elements_xpath, list):
        found_element = False
        for main_element in click_elements_xpath:
            try:
                elements = driver.find_elements(By.XPATH, main_element)
                for element in elements:
                    driver.execute_script(click_element_script, element)
                    found_element = True
                    break
                if found_element:
                    break
            except NoSuchElementException:
                continue
    else:
        try:
            elements = driver.find_elements(By.XPATH, click_elements_xpath)
            for element in elements:
                driver.execute_script(click_element_script, element)
                break
        except NoSuchElementException:
            pass


def get_y_location_by_scroll(driver, elements_xpath_list):
    # driver.implicitly_wait(10)
    from_element_xpath = elements_xpath_list[0]
    to_element_xpath = elements_xpath_list[1]
    position = {"from_position": None, "to_position": None}
    window_size = driver.get_window_size()
    screen_height = window_size["height"]
    current_scroll_position = 0

    while True:
        if from_element_xpath:
            from_element = driver.find_elements(By.XPATH, from_element_xpath)
            from_location = from_element[0].location["y"]
            position["from_position"] = from_location / screen_height * 100
        if to_element_xpath:
            to_element = driver.find_elements(By.XPATH, to_element_xpath)
            to_location = to_element[0].location["y"]
            position["to_position"] = to_location / screen_height * 100
            break
        if current_scroll_position == driver.execute_script(
            "return window.pageYOffset;"
        ):
            break
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        current_scroll_position = driver.execute_script("return window.pageYOffset;")
    return position


def scroll_to_relative_position(driver, position_a=0, position_b=1):
    # driver.implicitly_wait(5)
    scroll_height = driver.execute_script("return document.body.scrollHeight;")
    scroll_position_a = int(scroll_height * position_a / 100)
    scroll_position_b = int(scroll_height * position_b / 100)
    script = f"window.scrollTo(0, {scroll_position_a});"
    driver.execute_script(script)
    script = f"window.scrollTo(0, {scroll_position_b});"
    driver.execute_script(script)


def get_scroll(driver, scroll_percent=1):
    scroll_percent = max(0, min(scroll_percent, 100))
    screen_height = driver.execute_script("return window.innerHeight")
    scroll_length = int(screen_height * (scroll_percent / 100))
    driver.execute_script(f"window.scrollBy(0, {scroll_length});")


def get_values_of_element_by_method(driver, values_method_list, time_wait=10):
    # values_method_list = {"element_xpath": "element_xpath", "method": "text or get_attribute..."}
    # driver.implicitly_wait(5)
    driver.implicitly_wait(time_wait)
    element_xpath, method = (
        values_method_list["element_xpath"],
        values_method_list["method"],
    )
    values = ""

    if not isinstance(values_method_list, dict):
        print("The values_method argument must be dict type")
        return values

    try:
        item_web_element = driver.find_element(By.XPATH, element_xpath)
        match method:
            case "text":
                values = item_web_element.text
            case "get_attribute_href":
                values = item_web_element.get_attribute("href")
            case "get_attribute_title":
                values = item_web_element.get_attribute("title")
            case "get_attribute_img_src":
                values = item_web_element.get_attribute("src")
            case _:
                values = ""
    except NoSuchElementException:
        print(f"Not found the {element_xpath}")

    return values


def crawl_data_from_table_extent(driver, time_wait=10):
    table_data = []
    div_tbody_path = "//div[@class='db-table-body']"
    div_total_rows_path = div_tbody_path + "/div"

    driver.implicitly_wait(time_wait)
    rows_web_element = driver.find_elements(By.XPATH, div_total_rows_path)
    rows = len(rows_web_element)

    index = 1
    while index <= rows:
        tableData = read_json_file('D:\DEBANK\data', 'TableData.json')
        try:
            print(f"row: {index}")

            div_row_path = div_tbody_path + "/div[{}]/div[@class='db-table-row']"

            div_tcell_one_path = div_row_path + "/div[1]"
            div_tcell_user_address_path = (
                div_tcell_one_path + "/descendant::div[@class='db-user-row']/descendant::div[@class='db-user-name is-address']"
            )
            div_tcell_user_name_path = (
                div_tcell_one_path + "/descendant::div[@class='db-user-row']/descendant::div[@class='db-user-name is-web3']"
            )
            div_tcell_taglisst_path = (
                div_tcell_one_path + "/descendant::div[@class='db-user-tag-list']"
            )
            values_method_address = {
                "element_xpath": div_tcell_user_address_path.format(index),
                "method": "get_attribute_title",
            }
            values_method_name = {
                "element_xpath": div_tcell_user_name_path.format(index),
                "method": "get_attribute_title",
            }
            values_method_taglist = {
                "element_xpath": div_tcell_taglisst_path.format(index),
                "method": "text",
            }
            user_address = get_values_of_element_by_method(
                driver, values_method_address, time_wait
            )
            user_name = get_values_of_element_by_method(
                driver, values_method_name, time_wait
            )
            user_taglist = get_values_of_element_by_method(
                driver, values_method_taglist, time_wait
            )

            div_tcell_two_path = div_row_path + "/div[2]"
            div_tcell_networth_path = div_tcell_two_path + "/div"
            values_method_networth = {
                "element_xpath": div_tcell_networth_path.format(index),
                "method": "text",
            }
            networth = get_values_of_element_by_method(driver, values_method_networth, time_wait)

            div_tcell_three_path = div_row_path + "/div[3]"
            div_tcell_top_tokens_path = div_tcell_three_path + "/div"
            tokens_web = driver.find_elements(
                By.XPATH, div_tcell_top_tokens_path.format(index)
            )
            amount_tokens = len(tokens_web) + 1

            top_tokens = []
            if amount_tokens:
                for token_index in range(1, amount_tokens):
                    div_token_img_url_path = div_tcell_top_tokens_path + "/div[{}]/img"
                    div_token_percent_path = div_tcell_top_tokens_path + "/div[{}]"

                    values_method_token_img_url = {
                        "element_xpath": div_token_img_url_path.format(
                            index, token_index
                        ),
                        "method": "get_attribute_img_src",
                    }
                    values_method_token_percent = {
                        "element_xpath": div_token_percent_path.format(
                            index, token_index
                        ),
                        "method": "text",
                    }

                    token_img_url = get_values_of_element_by_method(
                        driver, values_method_token_img_url, time_wait
                    )
                    token_percent = get_values_of_element_by_method(
                        driver, values_method_token_percent, time_wait
                    )

                    token_info = {
                        "token_img_url": token_img_url,
                        "token_percent": token_percent,
                    }
                    top_tokens.append(token_info)

            div_tcell_four_path = div_row_path + "/div[4]"
            div_tcell_top_protocols_path = div_tcell_four_path + "/div"
            protocols_web = driver.find_elements(
                By.XPATH, div_tcell_top_protocols_path.format(index)
            )
            amount_protocols = len(protocols_web) + 1

            top_protocols = []
            if amount_protocols:
                for protocol_index in range(1, amount_protocols):
                    div_protocol_img_url_path = (
                        div_tcell_top_protocols_path + "/div[{}]/img"
                    )
                    div_protocol_percent_path = (
                        div_tcell_top_protocols_path + "/div[{}]"
                    )

                    values_method_protocol_img_url = {
                        "element_xpath": div_protocol_img_url_path.format(
                            index, protocol_index
                        ),
                        "method": "get_attribute_img_src",
                    }
                    values_method_protocol_percent = {
                        "element_xpath": div_protocol_percent_path.format(
                            index, protocol_index
                        ),
                        "method": "text",
                    }

                    protocol_img_url = get_values_of_element_by_method(
                        driver, values_method_protocol_img_url, time_wait
                    )
                    protocol_percent = get_values_of_element_by_method(
                        driver, values_method_protocol_percent, time_wait
                    )

                    protocol_info = {
                        "protocol_img_url": protocol_img_url,
                        "protocol_percent": protocol_percent,
                    }
                    top_protocols.append(protocol_info)

            table_row = {
                "user_address": user_address,
                "user_name": user_name,
                "user_taglist": user_taglist,
                "networth": networth,
                "top_tokens": top_tokens,
                "top_protocols": top_protocols,
            }

            print(table_row)
            table_data.append(table_row)
            tableData.append(table_row)
            write_json_file('D:\DEBANK\data', 'TableData.json', tableData)
            index += 1
        except NoSuchElementException:
            index += 1

    return table_data


def single_object_crawl(url, time_wait=10, driver=None):
    data = []

    if driver is None:
        driver = create_driver()

    go_to_web_url(driver, url)
    sleep_milliseconds(3000)

    driver.implicitly_wait(time_wait)

    last_page_index = get_last_page(driver, None)
    print(f"The Last page: {last_page_index[1]}")
    last_page_number = 2

    if not last_page_index[0]:
        last_page_number = last_page_index[1] + 1

    page_index = 1
    while page_index <= last_page_number:
        try:
            get_scroll(driver, 100)
            print(f"Start Crawling page {page_index}/{last_page_index[1]}")
            current_table_data = crawl_data_from_table_extent(driver)
            data.extend(current_table_data)
            page_index += 1
            page_element_xpath = "//ul/li[@title='{}']"
            click_element_xpath = page_element_xpath.format(page_index)
            click_element_by_script(driver, click_element_xpath)
            sleep_milliseconds(1500)
            driver.refresh()
            sleep_milliseconds(1500)
            get_scroll(driver, 0)
        except NoSuchElementException:
            page_index += 1

    return data


# def multi_object_crawl(file, args, stop_loop_condition, driver=None):
#     data = []
#     result_data = read_write_file_json(file["input_file"]["input_file_name"], file["input_file"]["action"])
#
#     if driver is None:
#         driver = create_driver()
#
#     name_key = None
#     url_key = None
#
#     for key in result_data[0].keys():
#         if "name" in key:
#             name_key = key
#         if "url" in key:
#             url_key = key
#
#     count_item = 1
#     for dict_item in result_data:
#         url = dict_item[url_key]
#         name = dict_item[name_key]
#         try:
#             print(f"Start Crawling Item {count_item}/{len(result_data)}")
#             out_file = single_object_crawl(url, 10, driver)
#             data.append({
#                 name_key: name,
#                 "data": out_file
#             })
#             count_item += 1
#         except NoSuchElementException:
#             print(f"There is problem from {url}")
#             continue
#
#     return data


def get_day_of_week_number():
    current_time = datetime.now()
    day_of_week_number = current_time.weekday()
    return day_of_week_number


def list_subfolders_and_files(
    folder_path, option="subfolder", wanted_item=None, unwanted_items=None
):
    subfolders_and_files = []

    try:
        if not os.path.isdir(folder_path):
            print(f"The folder of {folder_path} not exist")
            return []

        if option not in ["subfolder", "subfolder_and_file"]:
            raise ValueError(
                "Invalid 'option' value. It must be either 'subfolder' or 'subfolder_and_file'."
            )

        if wanted_item is None and unwanted_items is None:
            unwanted_items = {"folder_name": [".idea", "Root"], "file_name": None}

        for item in os.scandir(folder_path):
            if item.is_dir():
                if (
                    unwanted_items["folder_name"] is None
                    or item.name not in unwanted_items["folder_name"]
                ):
                    new_item = {"subfolder_name": item.name}
                    if option == "subfolder_and_file":
                        new_item["file_name"] = []
                        for sub_item in os.scandir(item.path):
                            if (
                                unwanted_items["file_name"] is None
                                or sub_item.name not in unwanted_items["file_name"]
                            ):
                                new_item["file_name"].append(sub_item.name)
                else:
                    continue
            elif item.is_file() and (
                unwanted_items["file_name"] is None
                or item.name not in unwanted_items["file_name"]
            ):
                parent_folder = os.path.basename(os.path.dirname(item.path))
                new_item = {"subfolder_name": parent_folder, "file_name": item.name}
            else:
                continue

            subfolders_and_files.append(new_item)

        return subfolders_and_files

    except OSError as e:
        print("There are errors:", e)
        return []


def check_exist_folder(parent_folder_path, folder_name):
    folder_path = os.path.join(parent_folder_path, folder_name)
    try:
        return os.path.exists(folder_path)
    except OSError as e:
        print("There are an errors:", e)
        return False


def read_json_file(absolute_file_path, file_name):
    if file_name is None:
        file_json = absolute_file_path
    else:
        file_json = os.path.join(absolute_file_path, file_name)

    try:
        with open(file_json, "r") as json_file:
            data = json.load(json_file)
        return data
    except FileNotFoundError:
        print(f"The file '{file_json}' does not exist.")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON in '{file_json}': {e}")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file '{file_json}': {e}")
        return None


def write_json_file(absolute_file_path, file_name, data):
    file_json = None
    if file_name is None:
        file_json = absolute_file_path
    elif ".json" in file_name:
        file_json = os.path.join(absolute_file_path, file_name)
    elif ".json" not in file_name:
        file_json = os.path.join(absolute_file_path, file_name + ".json")

    try:
        with open(file_json, "w") as json_file:
            json.dump(data, json_file)
        print(f"Data saved to '{file_json}' successfully.")
        return True
    except Exception as e:
        print(f"An error occurred while writing to the file '{file_json}': {e}")
        return False


def write_excel_file(folder_path, file_name, data):
    if ".xlsx" not in file_name:
        excel_file_path = os.path.join(folder_path, file_name + ".xlsx")
    else:
        excel_file_path = os.path.join(folder_path, file_name)
    # df = pd.DataFrame(data)
    if isinstance(data, list):
        df = pd.DataFrame(data)
        # if len(data) > 0 and isinstance(data[0], dict):
        #     df = pd.DataFrame(data)
        # elif len(data) > 0 and isinstance(data[0], list):
        #     df = pd.DataFrame(data[1:], columns=data[0])
        # else:
        #     raise ValueError("Data không hợp lệ. Phải là danh sách các từ điển hoặc danh sách 2 chiều.")
    else:
        raise ValueError("Data must be list of dict")

    df.to_excel(excel_file_path, index=False)


def create_folder(parent_folder_path, folder_name):
    folder_path = os.path.join(parent_folder_path, folder_name)
    try:
        if os.path.exists(folder_path):
            return True
        else:
            os.makedirs(folder_path)
            print(f"Đã tạo thư mục '{folder_name}' trong '{parent_folder_path}'.")
            return False
    except OSError as e:
        print("Đã xảy ra lỗi:", e)
        return False


def get_current_date_string():
    current_time = datetime.now()
    date_string = current_time.strftime("%Y%m%d")
    return date_string


def rename_file(rename_dict):
    old_name = rename_dict.get("org_name")
    new_name = rename_dict.get("new_name")

    if not old_name or not new_name:
        print(
            "Lỗi: Đối số không hợp lệ. Vui lòng cung cấp 'org_name' và 'new_name' trong từ điển."
        )
        return

    if not os.path.exists(old_name):
        print(f"Lỗi: File '{old_name}' không tồn tại.")
        return

    try:
        os.rename(old_name, new_name)
        print(f"Đã đổi tên file từ '{old_name}' thành '{new_name}'.")
    except Exception as e:
        print(f"Lỗi: {e}")


def is_valid_subfolder_name(name):
    try:
        int(name)
        return True
    except ValueError:
        return False


def create_folder_name(inputString, oldValue, newValue, convertInvalidChartTo="_"):
    invalid_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "."]
    temp = inputString.strip()
    outputString = temp.replace(oldValue, newValue)
    for character in outputString:
        if character in invalid_chars:
            outputString = outputString.replace(character, convertInvalidChartTo)
    return outputString


def sort_list_by_lower_name(e):
    name = e["token_name"].lower()
    return name


def sort_list_by_date(e):
    new_e = datetime.strptime(e["funding_date"], "%d-%m-%Y")
    return new_e
