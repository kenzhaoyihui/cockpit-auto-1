import time
from utils.page_objects import PageObject, PageElement, MultiPageElement


class DashboardPage(PageObject):
    """ To check Ovirt dashboard on Virtualization panel."""
    add_btn = PageElement(id_="dashboard-add")
    enable_btn = PageElement(id_="dashboard-enable-edit")
    cpu_link = PageElement(link_text="CPU")
    memory_link = PageElement(link_text="Memory")
    network_link = PageElement(link_text="Network")
    disk_link = PageElement(link_text="Disk I/O")

    # Elements after click the "add server" button
    add_address_input = PageElement(id_="add-machine-address")
    submit_btn = PageElement(class_name="btn-primary")
    cancel_btn = PageElement(class_name="btn-default")

    # Elements after click submit
    connect_btn = PageElement(class_name="btn_primary")
    user_input = PageElement(id_="login-custom-user")
    password_input = PageElement(id_="login-custom-password")
    login_btn = PageElement(class_name="btn-primary")

    # Elements under severs
    servers = MultiPageElement(class_name="host-label")

    # frame name
    frame_right_name = "cockpit1:localhost/dashboard"

    def __init__(self, *args, **kwargs):
        super(DashboardPage, self).__init__(*args, **kwargs)
        self.get("/dashboard")
        self.wait(period=5)

    def basic_check_elements_exists(self):
        with self.switch_to_frame(self.frame_right_name):
            assert self.cpu_link, "CPU button not exist"
            assert self.memory_link, "Memory button not exist"
            assert self.network_link, "Network button not exist"
            assert self.disk_link, "Disk button not exist"
            assert self.add_btn, "Add button not exist"
            assert self.enable_btn, "Edit button not exist"

    def check_cpu(self):
        """
        Purpose:
            Check cpu info by save screenshot of CPU link
        """
        with self.switch_to_frame(self.frame_right_name):
            self.cpu_link.click()
            time.sleep(120)
            self.save_screenshot("cpu_graph.png")

    def check_memory(self):
        """
        Purpose:
            Check memory info by save screenshot of Memory link
        """
        with self.switch_to_frame(self.frame_right_name):
            self.memory_link.click()
            time.sleep(120)
            self.save_screenshot("memory_graph.png")

    def check_network(self):
        """
        Purpose:
            Check network info by save screenshot of Network link
        """
        with self.switch_to_frame(self.frame_right_name):
            self.network_link.click()
            time.sleep(120)
            self.save_screenshot("network_graph.png")

    def check_disk_io(self):
        """
        Purpose:
            Check Disk IO info by save screenshot of Network link
        """
        with self.switch_to_frame(self.frame_right_name):
            self.disk_link.click()
            time.sleep(120)
            self.save_screenshot("disk_io_graph.png")

    def check_server_can_be_added(self, another_host, another_password):
        """
        Purpose:
            Check another server can be added to cockpit on dashboard page
        """
        with self.switch_to_frame(self.frame_right_name):
            self.add_btn.click()
            time.sleep(2)

            self.add_address_input.send_keys(another_host)
            time.sleep(2)
            self.submit_btn.click()
            time.sleep(1)

            try:
                self.connect_btn.click()
            except Exception:
                self.user_input.send_keys("root")
                self.password_input.send_keys(another_password)
                time.sleep(1)
                self.login_btn.click(1)
            finally:
                time.sleep(5)

            assert list(self.servers) == 2, "Failed to add another host"