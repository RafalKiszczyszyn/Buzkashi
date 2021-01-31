import datetime
import time

from django.contrib.auth import get_user_model
import sys
import time
from contextlib import contextmanager
from datetime import timedelta
from urllib.parse import urljoin

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from selenium import webdriver
try:
    from seleniumlogin import force_login
except ImportError:
    pass
from selenium.common import exceptions
from selenium.webdriver.support.ui import Select
from buzkashi_app.models import EduInstitution, Judge, Task, Competition, Team

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


@contextmanager
def suppress_stderr():
    "Temporarly suppress writes to stderr"

    class Null:
        write = lambda *args: None

    err, sys.stderr = sys.stderr, Null
    try:
        yield
    finally:
        sys.stderr = err


def exception_to_none(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except exceptions.NoSuchElementException:
        return None


class RegistrationViewTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(RegistrationViewTest, cls).setUpClass()
        cls.registration_url = urljoin(cls.live_server_url, '/registration')
        cls.success_url = urljoin(cls.live_server_url, '/registration/success')

    def setUp(self):
        institution1 = EduInstitution.objects.create(name='Szkoła średnia', region='Region', email='hs@example.com',
                                                     authorization_code='valid@code', is_university=False)
        self.high_school_id = str(institution1.id)

        institution2 = EduInstitution.objects.create(name='Uczelnia wyższa', region='Region', email='uni@example.com')
        self.university_id = str(institution2.id)

        competition1 = Competition.objects.create(title='Zawody A', session=Competition.Session.HIGH_SCHOOL_SESSION,
                                                  start_date=timezone.now() + timedelta(weeks=2),
                                                  duration=timedelta(hours=3),
                                                  is_test=False)
        self.high_school_comp_id = str(competition1.id)

        competition2 = Competition.objects.create(title='Zawody B',
                                                  start_date=timezone.now() + timedelta(weeks=2, days=1),
                                                  duration=timedelta(hours=3), is_test=False)
        self.university_comp_id = str(competition2.id)

        Team.objects.create(name='Rockersi', competition=competition1, institution=institution1)

        with suppress_stderr():
            self.browser = webdriver.Edge('./static/msedgedriver.exe')
            self.browser.implicitly_wait(3)

    def tearDown(self) -> None:
        with suppress_stderr():
            self.browser.quit()

    def init(self):
        self.inputs = {
            # participant1
            'id_form-0-name': 'Rafał',
            'id_form-0-surname': 'Kiszczyszyn',
            'id_form-0-email': 'kiszczyszyn@gmail.com',
            # participant2
            'id_form-1-name': 'Kaja',
            'id_form-1-surname': 'Limisiewicz',
            'id_form-1-email': 'limisiewicz@gmail.com',
            # participant3
            'id_form-2-name': 'Marek',
            'id_form-2-surname': 'Testowy',
            'id_form-2-email': 'testowy@gmail.com',
            # team
            'id_name': '',
            # compliment
            'id_authorization_code': '',
            'id_tutor_name': '',
            'id_tutor_surname': '',
            'id_priority': ''
        }

        self.browser.get(self.registration_url)

    def populate_inputs(self, **inputs):
        for id in inputs:
            self.browser.find_element_by_id(id).send_keys(inputs[id])

    def select_institution(self, id_value):
        select = Select(self.browser.find_element_by_id('id_institution'))
        select.select_by_value(id_value)

    def select_competition(self, id_value):
        select = Select(self.browser.find_element_by_id('id_competition'))
        select.select_by_value(id_value)

    def submit(self):
        self.browser.find_element_by_id('id_submit').click()

    def test_PT008(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id('topbar-button-register').click()
        self.submit()

        self.assertEqual(self.browser.current_url, self.registration_url)

    def test_PT009(self):
        self.init()
        self.inputs['id_form-0-email'] = 'invalid@email'
        self.inputs['id_form-1-email'] = 'invalid@email'
        self.inputs['id_form-2-email'] = 'invalid@email'
        self.inputs['id_name'] = 'Rockersi'
        self.populate_inputs(**self.inputs)
        self.select_institution(self.university_id)
        self.select_competition(self.university_comp_id)
        self.submit()

        self.assertIsNotNone(exception_to_none(self.browser.find_element_by_id, 'id_error-0-email'))
        self.assertIsNotNone(exception_to_none(self.browser.find_element_by_id, 'id_error-1-email'))
        self.assertIsNotNone(exception_to_none(self.browser.find_element_by_id, 'id_error-2-email'))
        self.assertIsNotNone(exception_to_none(self.browser.find_element_by_id, 'id_error-name'))

    def test_PT010(self):
        self.init()
        self.inputs['id_name'] = 'Unikalni'
        self.populate_inputs(**self.inputs)
        self.select_institution(self.university_id)
        self.select_competition(self.high_school_comp_id)
        self.submit()

        self.assertIsNotNone(exception_to_none(self.browser.find_element_by_id, 'id_error-competition'))

        self.select_institution(self.high_school_id)
        self.select_competition(self.university_comp_id)
        self.submit()

        self.assertIsNotNone(exception_to_none(self.browser.find_element_by_id, 'id_error-competition'))

    def test_PT011(self):
        self.init()
        self.inputs['id_name'] = 'Czarni rycerze'
        self.populate_inputs(**self.inputs)
        self.select_institution(self.university_id)
        self.select_competition(self.university_comp_id)
        self.submit()

        self.assertEqual(self.browser.current_url.split("?")[0], self.success_url)

    def test_PT012(self):

        pass

    def test_PT013(self):
        self.init()
        self.inputs['id_name'] = 'Szefostwo'
        self.inputs['id_authorization_code'] = 'valid@code'
        self.inputs['id_tutor_name'] = 'Adela'
        self.inputs['id_tutor_surname'] = 'Majewska'
        self.inputs['id_priority'] = '1'
        self.populate_inputs(**self.inputs)
        self.select_institution(self.high_school_id)
        self.select_competition(self.high_school_comp_id)
        self.submit()

        self.assertURLEqual(self.browser.current_url, self.success_url)
