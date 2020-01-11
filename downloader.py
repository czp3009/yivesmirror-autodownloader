import json
import sys
import urllib.request
from pathlib import Path

base_url = "https://yivesmirror.com/api/"
version = sys.version_info
ua = "python/%s.%s.%s" % (version.major, version.minor, version.micro)
opener = urllib.request.build_opener()
# noinspection SpellCheckingInspection
opener.addheaders = [("User-agent", ua)]
urllib.request.install_opener(opener)


def fetch(url: str):
    result = urllib.request.urlopen(url)
    return json.load(result)


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage:\npython downloader.py {outputDir} ...{option}")
    # parse args
    output_dir, *input_options = sys.argv[1:]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    print("Output directory: " + str(output_path.absolute()))
    print("Input options: " + str(input_options))
    select_all = "all" in input_options

    # fetch option list
    option_list = fetch(base_url + "list/all")
    print("Available options: " + str(option_list))
    if select_all:
        selected_options = option_list
    else:
        selected_options = list(set(input_options).intersection(set(option_list)))
    if not selected_options:
        sys.exit("No option selected")
    print("Selected: " + str(selected_options))

    # process option
    for option in selected_options:
        print("Processing " + option)
        option_path = output_path / option
        option_path.mkdir(parents=True, exist_ok=True)
        available_items = fetch("%s/list/%s" % (base_url, option))
        print("Available items: " + str(len(available_items)))
        missing_items = list(set(available_items).difference(set(map(lambda it: it.name, option_path.iterdir()))))
        missing_items.sort(reverse=True)
        missing_item_number = len(missing_items)
        print("Missing items: " + str(missing_item_number))
        if missing_item_number == 0:
            sys.exit("Everything up-to-date")
        for item in missing_items:
            file_info = fetch("%s/file/%s/%s" % (base_url, option, item))
            direct_link = file_info["direct_link"]
            print("Downloading: " + direct_link)
            file_path = option_path / file_info["file_name"]
            try:
                urllib.request.urlretrieve(direct_link, str(file_path))
            except BaseException:
                try:
                    file_path.unlink()
                except IOError:
                    pass
                raise


if __name__ == '__main__':
    main()
