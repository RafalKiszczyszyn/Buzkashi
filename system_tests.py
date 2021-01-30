import datetime
import time

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from seleniumlogin import force_login

from buzkashi_app.models import Judge, Task, Competition

USERNAME = 'nowy_user'
PASSWORD = 'zawody2k21'


def force_login_judge(browser, live_server):
    user = get_user_model().objects.create(username=USERNAME, password=PASSWORD)
    Judge.objects.create(user=user)

    force_login(user, browser, live_server)
    browser.get(live_server)


class JudgeViewTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('./static/chromedriver')
        self.browser.implicitly_wait(3)

    def tearDown(self) -> None:
        self.browser.close()

    def check_tasks_page(self):
        page_title_element = self.browser.find_element_by_id("tasks__title")
        task_create_button_element = self.browser.find_element_by_id("create-button")
        self.assertEqual("Zadania", page_title_element.text)
        self.assertIn('Dodaj nowe zadanie', task_create_button_element.get_attribute("value"))

    def check_task_tile(self, task_title):
        task = Task.objects.get(title=task_title)
        new_task_element = self.browser.find_element_by_id("tasks__tile-{}".format(task.id))
        self.assertIn(task_title, new_task_element.get_attribute("innerHTML"))
        self.assertIn("Edytuj zadanie", new_task_element.get_attribute("innerHTML"))
        self.assertIn("Dodaj testy akceptacyjne", new_task_element.get_attribute("innerHTML"))
        self.assertIn("Dodaj do zawodów", new_task_element.get_attribute("innerHTML"))

    def task_edit_send_keys(self, task_title, task_body):
        title_input_element = self.browser.find_element_by_id("id_title")
        body_input_element = self.browser.find_element_by_id("id_body")
        save_button_element = self.browser.find_element_by_id("task-edit__submit")

        title_input_element.clear()
        body_input_element.clear()

        title_input_element.send_keys(task_title)
        body_input_element.send_keys(task_body)

        save_button_element.click()

    def check_task_edit_page(self, task_title, task_body, placeholder):
        if placeholder:
            input_attribute = "placeholder"
        else:
            input_attribute = "value"

        page_title_element = self.browser.find_element_by_id("task-edit__title")
        title_input_element = self.browser.find_element_by_id("id_title")
        body_input_element = self.browser.find_element_by_id("id_body")
        save_button_element = self.browser.find_element_by_id("task-edit__submit")
        cancel_button_element = self.browser.find_element_by_id("task-edit__cancel")
        self.assertEqual("Edycja zadania", page_title_element.text)
        self.assertEqual(task_title, title_input_element.get_attribute(input_attribute))
        self.assertEqual(task_body, body_input_element.get_attribute(input_attribute))
        self.assertEqual("Anuluj", cancel_button_element.text)
        self.assertEqual("Zapisz zmiany", save_button_element.get_attribute("value"))

    def check_task_competition(self, task_title, comp_title, comp_session):
        task = Task.objects.get(title=task_title)
        task_comp_title = self.browser.find_element_by_id("tasks__tile__competition-title-{}".format(task.id))
        task_comp_session = self.browser.find_element_by_id("tasks__tile__session-{}".format(task.id))
        self.assertEqual(comp_title, task_comp_title.text)
        self.assertIn(comp_session, task_comp_session.get_attribute("innerHTML"))

    def check_task_edit_competition(self, comp_title, comp_session):
        task_comp_title_element = self.browser.find_element_by_id("task-edit__comp-title")
        task_comp_session_element = self.browser.find_element_by_id("task-edit__comp-session")
        self.assertEqual(comp_title, task_comp_title_element.text)
        self.assertIn(comp_session, task_comp_session_element.get_attribute("innerHTML"))

    def check_modal(self, task_title):
        modal_title_element = self.browser.find_element_by_id("modal__task-title")
        modal_content_element = self.browser.find_element_by_id("modal_tile-content")
        modal_select_input_element = self.browser.find_element_by_name("select-comp")
        modal_options_list = modal_select_input_element.find_elements_by_tag_name('option')
        modal_submit_button_element = self.browser.find_element_by_id("modal__tile-buttons__submit")

        self.assertEqual(task_title, modal_title_element.text)
        self.assertIn("Wybierz zawody, do których chcesz podpiąć zadanie",
                      modal_content_element.get_attribute("innerHTML"))
        self.assertEqual("---------", modal_options_list.pop().text)
        self.assertEqual("Zapisz", modal_submit_button_element.get_attribute("value"))

    def modal_send_keys(self, comp_title):
        modal_select_input_element = self.browser.find_element_by_name("select-comp")
        modal_options_list = modal_select_input_element.find_elements_by_tag_name('option')
        modal_submit_button_element = self.browser.find_element_by_id("modal__tile-buttons__submit")

        for option in modal_options_list:
            if option.text == comp_title:
                option.click()
                break

        modal_submit_button_element.click()

    def test_PT001(self):
        self.browser.get(self.live_server_url)
        nav_menu = self.browser.find_element_by_id("sidebar-menu").get_attribute("innerHTML")

        self.assertIn("Home", nav_menu)
        self.assertIn("Zawody", nav_menu)
        self.assertIn("Ranking", nav_menu)
        self.assertNotIn("Zadania", nav_menu)

        self.browser.get('{}/tasks/'.format(self.live_server_url))
        tile_title_element = self.browser.find_element_by_id("login-inputs__title")
        login_inputs_element = self.browser.find_element_by_id("login-inputs")
        self.assertEqual("Login", tile_title_element.text)
        self.assertIn('<input type="text" name="username"', login_inputs_element.get_attribute("innerHTML"))
        self.assertIn('<input type="password" name="password"', login_inputs_element.get_attribute("innerHTML"))

    def test_PT002(self):
        force_login_judge(self.browser, self.live_server_url)
        self.browser.get('{}/tasks/'.format(self.live_server_url))

        self.check_tasks_page()
        main_element = self.browser.find_element_by_tag_name("main")
        self.assertNotIn('<div id="tasks__tile', main_element.get_attribute("innerHTML"))

    def test_PT003(self):
        self.test_PT002()
        title = "camelCase"
        body = "Stwórz funkcję, która rozdzieli ciąg znaków pisanych notacją camelCase."

        task_create_button_element = self.browser.find_element_by_id("tasks__task-create-button")
        task_create_button_element.click()

        self.check_task_edit_page("Tytuł zadania", "Wprowadź treść zadania", True)
        self.task_edit_send_keys(title, body)

        self.check_tasks_page()
        self.check_task_tile(title)

    def test_PT004(self):
        self.test_PT002()
        title = ""
        body = ""

        task_create_button = self.browser.find_element_by_id("tasks__task-create-button")
        task_create_button.click()
        add_task_url = self.browser.current_url

        self.check_task_edit_page("Tytuł zadania", "Wprowadź treść zadania", True)
        self.task_edit_send_keys(title, body)

        self.assertEqual(add_task_url, self.browser.current_url)

    def test_PT005(self):
        self.test_PT003()
        task_title = "camelCase"
        task_new_comp_title = "Wiosenne starcie wrocławskich uczelni"
        task_object = Task.objects.get(title=task_title)
        Competition.objects.create(
            title=task_new_comp_title,
            duration=datetime.timedelta(seconds=10800),
            is_test=False
        )
        self.browser.refresh()

        self.check_tasks_page()
        self.check_task_tile(task_title)

        add_to_comp_button_element = self.browser.find_element_by_id(
            "tasks__tile__task-buttons__competition-{}".format(task_object.id))
        add_to_comp_button_element.click()

        self.check_modal(task_title)
        self.modal_send_keys(task_new_comp_title)

        self.check_task_competition(task_title, task_new_comp_title, "Sesja dla studentów")

    def test_PT006(self):
        self.test_PT005()
        task_title = "camelCase"
        task_comp_title = "Wiosenne starcie wrocławskich uczelni"

        task_object = Task.objects.get(title=task_title)

        self.check_tasks_page()
        self.check_task_tile(task_title)
        self.check_task_competition(task_title, task_comp_title, "Sesja dla studentów")

        add_to_comp_button_element = self.browser.find_element_by_id(
            "tasks__tile__task-buttons__competition-{}".format(task_object.id))
        add_to_comp_button_element.click()

        self.check_modal(task_title)
        self.modal_send_keys("---------")

        self.check_task_competition(task_title, "", "")

    def test_PT007(self):
        self.test_PT005()
        task_title = "camelCase"
        task_old_body = "Stwórz funkcję, która rozdzieli ciąg znaków pisanych notacją camelCase."
        task_new_body = "Stwórz funkcję, która rozdzieli ciąg znaków pisanych notacją camelCase." \
                        "Przykład:‘camelCase’: ‘camel case’"
        task_comp_title = "Wiosenne starcie wrocławskich uczelni"
        task_object = Task.objects.get(title=task_title)

        task_edit_button_element = self.browser.find_element_by_id(
            "tasks__tile__task-buttons__edit-{}".format(task_object.id))

        task_edit_button_element.click()

        self.check_task_edit_page(task_title, task_old_body, False)
        self.check_task_edit_competition(task_comp_title, "Sesja dla studentów")
        self.task_edit_send_keys(task_title, task_new_body)

        self.check_task_tile(task_title)

        tasks_edited_task_body_element = \
            self.browser.find_element_by_id("tasks__tile__task-body-{}".format(task_object.id))
        self.assertIn(task_new_body, tasks_edited_task_body_element.get_attribute("innerHTML"))
