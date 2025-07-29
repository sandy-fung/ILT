from Controller import Controller
from ILT_UI import UI
from log_levels import DEBUG, INFO, ERROR
from UI_event import UIEvent

def main():

    ui = UI()
    controller = None
    
    def dispatcher(event_type, event_data):
        nonlocal controller

        if controller:
            controller.handle_event(event_type, event_data)

        elif event_type == UIEvent.RESELECT_BT_CLICK:
            try:
                controller = Controller(ui)
                #controller.handle_event(UIEvent.WINDOW_READY, {})
            except Exception as e:
                ERROR("Error reinitializing controller:", e)
                ui.show_error(str(e))
    
    ui.set_dispatcher(dispatcher)
    
    try:
        controller = Controller(ui)
    except Exception as e:
        if hasattr(e, 'winerror') and e.winerror == 3:
            ERROR("Can't find the the path specified.")
            ui.show_error("找不到檔案路徑，請確認 config.ini 是否存在，或重新設定路徑。")
        else:
            ERROR("Error checking config:", e)
            ui.show_error(e)

    ui.run()

if __name__ == "__main__":
    main()