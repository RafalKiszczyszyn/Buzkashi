import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver


class JudgeViewTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('./static/chromedriver')
        self.browser.implicitly_wait(3)

    def tearDown(self) -> None:
        self.browser.close()

    def test_if_sidebar_home_works(self):
        initial_url = self.live_server_url
        self.browser.get(initial_url)
        sidebar_menu_home = self.browser.find_element_by_id('sidebar-home')
        sidebar_menu_home.click()
        self.assertEqual(initial_url, self.live_server_url)
        sidebar_menu_button = self.browser.find_element_by_id('btn-sidebar')
        sidebar_menu_button.click()
        time.sleep(5)
        sidebar_menu_button.click()

    def test_if_sidebar_tasks_works(self):
        initial_url = self.live_server_url
        self.browser.get(initial_url)
        sidebar_menu_rank = self.browser.find_element_by_id('sidebar-rank')
        sidebar_menu_rank.click()
        time.sleep(10)
