from Controler import Controller
from ILT_UI import UI

if __name__ == "__main__":
    def dispatcher(event_type, event_data):
        Controller.handle_event(event_type, event_data)

    ui = UI(dispatcher)
    controller = Controller(ui)
    ui.run() 