from Controller import Controller
from ILT_UI import UI

controller = None
def dispatcher(event_type, event_data):
    controller.handle_event(event_type, event_data)

if __name__ == "__main__":


    ui = UI(dispatcher)
    controller = Controller(ui)
    ui.run() 