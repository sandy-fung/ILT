from Controller import Controller
from ILT_UI import UI
from log_levels import DEBUG, INFO, ERROR



def main():

    ui = UI()
    def dispatcher(event_type, event_data):
        controller.handle_event(event_type, event_data)
    try:
        controller = Controller(ui)
    except Exception as e:
        ERROR("Error checking config:", e)
        ui.show_error(e)

    ui.set_dispatcher(dispatcher)

    ui.run()

if __name__ == "__main__":
    main()