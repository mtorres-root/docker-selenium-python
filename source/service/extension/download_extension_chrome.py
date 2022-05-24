import re

from interface.extension.extension_manager import ExtensionManager
from service.user_agent_browser import UserAgentBrowser


class DownloadExtensionChrome(ExtensionManager):
    extension = "crx"
    path_file = "extensions/chrome"
    path_assets = None
    browser = 'chrome'
    driver = None

    def __init__(self, path_assets):
        super().__init__()
        self.path_assets = path_assets
        self.path_file = f"{path_assets}/{self.path_file}"

    def _get_user_agent_browser(self):
        user_agent_browser = UserAgentBrowser(self.path_assets, self.browser, self.driver)
        return user_agent_browser.data_user_agent()

    def _get_version(self, user_agent):
        response = {"major": "", "minor": "", "build": "", "patch": ""}
        # Get Version
        regex = r"Chrom(?:e|ium)\/([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)"
        matches = re.finditer(regex, user_agent, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            match_value = match.group()
            if match_value:
                code_value = match_value.split("/")[-1]
                if code_value:
                    value = code_value.split(".")
                    if len(value) == 4:
                        response = {
                            "major": value[0],
                            "minor": value[1],
                            "build": value[2],
                            "patch": value[3],
                        }
        # Make Again version
        version = (
                response["major"]
                + "."
                + response["minor"]
                + "."
                + response["build"]
                + "."
                + response["patch"]
        )
        # Return version
        return version

    def _get_arch(self, user_agent):
        nacl_arch = "arm"
        if user_agent.find("x86") > 0:
            nacl_arch = "x86-32"
        elif user_agent.find("x64") > 0:
            nacl_arch = "x86-64"
        return nacl_arch

    def _make_url(self, id_extension):
        user_agent = self._get_user_agent_browser()
        version = self._get_version(user_agent)
        nacl_arch = self._get_arch(user_agent)
        url = (
            "https://clients2.google.com/service/"
            "update2/crx?response=redirect"
            "&prodversion={version}&acceptformat=crx2,crx3&x=id%3D{"
            "id_extension}%26uc&nacl_arch={nacl_arch}".format(
                version=version, id_extension=id_extension, nacl_arch=nacl_arch
            )
        )
        return url

    def _get_info(self, url_base_extension):
        data_main = url_base_extension.split("/")
        extension_id = data_main[-1]
        extension_name = data_main[-2]
        file_name = "{name_extension}.{extension}".format(
            name_extension=extension_name, extension=self.extension
        )
        return {
            "extension_id": extension_id,
            "extension_name": extension_name,
            "file_name": file_name,
        }

    def _get_data_extension(self, url_ext):
        info_extension = self._get_info(url_ext)
        path_file = self._get_path_extension(url_ext, info_extension)
        url = self._make_url(info_extension["extension_id"])
        return {"url": url, "path_file": path_file}

    def generate_extension(self, url):
        data = self._get_data_extension(url)
        url = data["url"]
        path_file = data["path_file"]
        self._download_extension(url, path_file)
        return data["path_file"]
