from InquirerPy import inquirer
import threading
import os
import time
import keyboard
import pyautogui as pag
import pydirectinput as pdi
import numpy as np
import cv2
import random
import mss

pdi.PAUSE = 0.001
confidence_val = 0.7
operation_state = None
sell_ores = []
pause = False

def sell_ore():
    ores = []
    for ore in os.listdir('img_data/sell_ores'):
        if ore.endswith('.png'):
            ore = ore.replace('.png', '')
            ores.append(ore)
    return ores 

def search_img_maxslot():
    try:
        location = pag.locateOnScreen('img_data/data/max_slot.png', confidence= confidence_val, grayscale=True)
        return location and True or False
    except:
        return False

def sell_item(name):
    try:
        item_location = pag.locateOnScreen(f'img_data/sell_ores/{name}.png', confidence= 0.8, grayscale=True)
        if item_location:
            item_location = pag.center(item_location)
            pdi.moveTo(item_location.x, item_location.y)
            pdi.moveRel(1, 1)
            pdi.click()
            time.sleep(0.8)
            maxbtn_location = pag.locateOnScreen('img_data/data/max.png', confidence= confidence_val, grayscale=True)
            if maxbtn_location:
                maxbtn_location = pag.center(maxbtn_location)
                pdi.moveTo(maxbtn_location.x, maxbtn_location.y)
                pdi.moveRel(1, 1)
                pdi.click()
                time.sleep(0.8)
                selectbtn_location = pag.locateOnScreen('img_data/data/select.png', confidence= confidence_val, grayscale=True)
                if selectbtn_location:
                    selectbtn_location = pag.center(selectbtn_location)
                    pdi.moveTo(selectbtn_location.x, selectbtn_location.y)
                    pdi.moveRel(1, 1)
                    pdi.click()
                    time.sleep(0.8)
                    return True
    except:
        return False    

def press_btn(btn):
    try:
        btn_location = pag.locateOnScreen(f'img_data/data/{btn}.png', confidence= confidence_val, grayscale=True)
        if btn_location:
            btn_location = pag.center(btn_location)
            pdi.moveTo(btn_location.x, btn_location.y)
            pdi.moveRel(1, 1)
            pdi.click()
            time.sleep(2)
            return True
    except:
        return False


def select_operation():
    if operation_state is None:
        operation = inquirer.select(
            message="Select an operation:",
            choices=[
                "Auto Forge",
                "Auto Mine",
            ],
        ).execute()
        if operation == "Auto Forge":
            auto_forge()
        elif operation == "Auto Mine":
            auto_mine()

def pause_program():
    while True:
        if keyboard.is_pressed('p'):
            global pause
            pause = not pause
            if pause:
                print("Auto Mine Pause. (Press 'p' to Resume)")
            else:
                print("Auto Mine Resume. (Press 'p' to Pause)")
        time.sleep(0.1)

def auto_forge():
    print("Auto Forge Start. (Press 'ctrl+x' to Stop)")
    with mss.mss() as sct:
        lower_green = np.array([0, 255, 0])
        upper_green = np.array([0, 255, 0])
        monitor = sct.monitors[1]

        region = {'left': 430, 'top': 170, 'width': 1700, 'height': 1100}
        while True:
            img = np.array(sct.grab(region))
            img_bgr = img[:, :, :3]
            mask = cv2.inRange(img_bgr, lower_green, upper_green)
            x, y, w, h = cv2.boundingRect(mask)
            
            if w > 50 and h > 50:
                center_x = x + w // 2
                center_y = y + h // 2
                screen_x = center_x + monitor['left'] + region['left']
                screen_y = center_y + monitor['top'] + region['top']
                pdi.moveTo(screen_x, screen_y)
                pdi.click()
            if keyboard.is_pressed('ctrl+x'):
                pdi.mouseUp(button='left')
                break
        cv2.destroyAllWindows()
        return select_operation()

def auto_mine():
    print("Auto Mine Start. (Press 'p' to Pause / Press 'ctrl+x' to Stop)")
    threading.Thread(target=pause_program).start()
    time.sleep(3)
    while True:
        failed_sell = []
        isItemFull = search_img_maxslot()
        if not isItemFull:
            if not pause:
                pdi.click()
            time.sleep(random.randint(10, 20)*0.01)
        else:
            pdi.press('t')
            time.sleep(2.5)
            sellbtn_location = pag.locateOnScreen('img_data/data/sell_item.png', confidence= confidence_val, grayscale=True)
            if sellbtn_location:
                sellbtn_location = pag.center(sellbtn_location)
                pdi.moveTo(sellbtn_location.x, sellbtn_location.y)
                pdi.moveRel(1, 1)
                pdi.click()
                time.sleep(1)
                for item in sell_ores:
                    selled = sell_item(item)
                    if selled:
                        continue
                    else:
                        failed_sell.append(item)
                if failed_sell:
                    pdi.moveTo(961, 670)
                    pdi.moveRel(1, 1)
                    pag.scroll(-130)
                    pdi.moveRel(1, 1)
                    for item in failed_sell:
                        selled = sell_item(item)
                        if selled:
                            continue
                press_btn('accept')
                time.sleep(1)
                press_btn('yes')
                time.sleep(1)
                press_btn('close')
        if keyboard.is_pressed('ctrl+x'):
            print("Auto Mine Stop.")
            return select_operation()

if __name__ == '__main__':
    try:
        sell_ores = sell_ore()
        select_operation()
    except KeyboardInterrupt:
        print("\nGoodbye!")