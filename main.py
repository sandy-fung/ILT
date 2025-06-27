from Controller import Controller
from ILT_UI import UI


if __name__ == "__main__":
    ui = UI()
    def dispatcher(event_type, event_data):
        controller.handle_event(event_type, event_data)
    controller = Controller(ui)
    ui.set_dispatcher(dispatcher)
    ui.run()