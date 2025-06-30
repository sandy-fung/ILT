from Controller import Controller
from ILT_UI import UI
import log_levels



def main():

    ui = UI()
    def dispatcher(event_type, event_data):
        controller.handle_event(event_type, event_data)
    controller = Controller(ui)
    ui.set_dispatcher(dispatcher)

    ui.run()

if __name__ == "__main__":
    main()