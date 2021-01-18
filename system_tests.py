from urllib.parse import urljoin
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver


class JudgeViewTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('./static/chromedriver')
        self.browser.implicitly_wait(3)

    def tearDown(self) -> None:
        self.browser.close()

    def test_login(self):
        base_url = self.live_server_url
        self.browser.get(base_url)
        login_button = self.browser.find_element_by_id('topbar-button-login')
        login_button.click()

        input_login = self.browser.find_element_by_id('id_username')
        input_login.send_keys('limi')
        input_password = self.browser.find_element_by_id('id_password')
        input_password.send_keys('limi')
        submit_button = self.browser.find_element_by_id('submit-button')
        submit_button.click()

    def test_sidebar_rank_button(self):
        self.browser.get(self.live_server_url)
        sidebar_menu_rank = self.browser.find_element_by_id('sidebar-rank')
        sidebar_menu_rank.click()

        self.assertEqual(self.browser.current_url, urljoin(self.live_server_url, '/rank/'))
