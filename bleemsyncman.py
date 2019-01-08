#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# mount -o umask=000 -t vfat /dev/sdc1 /mnt
# mount -o umask=000 `findmnt -n -U -o SOURCE --target /mnt` /mnt
# MNTDEV=`findmnt -n -U -o SOURCE --target /mnt`; umount $MNTDEV; mount -o umask=000,exec -t vfat $MNTDEV /mnt
# MNTDEV=`findmnt -n -U -o SOURCE --target /media/sng/SONY` && sudo umount $MNTDEV && sudo mkdir -p /media/sng/SONY && sudo mount -o umask=000,exec -t vfat $MNTDEV /media/sng/SONY
# MNTDEV=`findmnt -n -U -o SOURCE --target /media/sng/SONY3` && sudo umount $MNTDEV && sudo mkdir -p /media/sng/SONY3 && sudo mount -o umask=000,exec -t vfat $MNTDEV /media/sng/SONY3

# mkdosfs /dev/sdc1 -s 64 -F 32 -n SONY
# pyinstaller --onefile --noconsole bleemsyncman.py

import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import os
import platform
import subprocess
import errno
import pprint
import threading
import time
import shutil
import string
import base64
import sys
import re
import pyunpack
import patoolib
import tempfile
import traceback
import zlib
import io
import webbrowser

from PIL import Image, ImageTk, ImageOps
from operator import itemgetter


if __name__ != '__main__':
    print('Do not import this file, just run.')
    exit(1)

if sys.version_info[0] < 3 or sys.version_info[1] < 5:
    print('Python 3.5+ is required.')
    exit(2)


HOMEPAGE_URL = 'https://github.com/skazanyNaGlany/BleemSyncMan'
GAMES_DELETED_DIR = 'Games.deleted'

BGT_STATE_NONE = 1
BGT_STATE_APPLY_CHANGES = 2
BGT_STATE_ADD_GAME = 3
BGT_STATE_UNPACK_FILE = 4

COVER_ART_WIDTH = 226
COVER_ART_HEIGHT = 226

# run time variables
games_list = []
current_directory = None
buttons_enabled = True
background_thread = None
background_thread_run = True
background_thread_states = []
on_add_game_button_click_user_data = {}

WINDOW_TITLE = 'BleemSyncMan v0.1'
GAME_INI_TMP = '''[Game]
Discs={discs}
Title={title}
Publisher={publisher}
Players={players}
Year={year}
'''
PCSX_CFG_TMP = '''Bios = SET_BY_PCSX
Gpu3 = builtin_gpu
Spu = builtin_spu
Xa = 0
Mdec = 0
Cdda = 0
Debug = 0
PsxOut = 0
SpuIrq = 0
RCntFix = 0
VSyncWA = 0
Cpu = 0
region = 0
g_scaler3 = 2
g_gamma = 64
g_layer_x = 0
g_layer_y = 0
g_layer_w = 0
g_layer_h = 0
soft_filter = 0
scanlines = 0
scanline_level = 14
plat_target.vout_method = 1
plat_target.hwfilter = 0
plat_target.vout_fullscreen = 0
state_slot = 0
cpu_clock = ffffffff
g_opts = 00
in_type_sel1 = 0
in_type_sel2 = 0
analog_deadzone = 32
memcard1_sel = ffffffff
memcard2_sel = ffffffff
g_autostateld_opt = 0
open_invalid_time = 16
adev0_is_nublike = 0
adev1_is_nublike = 0
frameskip3 = 0
gpu_peops.iUseDither = 0
gpu_peops.dwActFixes = 80
gpu_unai.lineskip = 0
gpu_unai.abe_hack = 0
gpu_unai.no_light = 0
gpu_unai.no_blend = 0
gpu_neon.allow_interlace = 2
gpu_neon.enhancement_enable = 0
gpu_neon.enhancement_no_main = 0
gpu_peopsgl.bDrawDither = 0
gpu_peopsgl.iFilterType = 0
gpu_peopsgl.iFrameTexType = 0
gpu_peopsgl.iUseMask = 0
gpu_peopsgl.bOpaquePass = 0
gpu_peopsgl.bAdvancedBlend = 0
gpu_peopsgl.bUseFastMdec = 0
gpu_peopsgl.iVRamSize = 40
gpu_peopsgl.iTexGarbageCollection = 1
gpu_peopsgl.dwActFixes = 0
spu_config.iUseReverb = 1
spu_config.iXAPitch = 0
spu_config.iUseInterpolation = 1
spu_config.iTempo = 0
spu_config.iUseThread = 1
config_save_counter = 4
in_evdev_allow_abs_only = 0
volume_boost = 0
psx_clock = 39
new_dynarec_hacks = 0
in_enable_vibration = 0
binddev = sdl:keys
bind escape = Enter Menu
bind backspace = Fast Forward
bind c = player1 SELECT
bind d = player1 TRIANGLE
bind e = player1 L2
bind r = player1 R1
bind s = player1 SQUARE
bind t = player1 R2
bind v = player1 START
bind w = player1 L1
bind x = player1 CIRCLE
bind z = player1 CROSS
bind f1 = Save State
bind f2 = Load State
bind f3 = Prev Save Slot
bind f4 = Next Save Slot
bind f5 = Toggle Frameskip
bind f6 = Take Screenshot
bind f7 = Show/Hide FPS
bind f8 = Switch Renderer
bind f9 = CD Change button
bind f10 = RESET button
bind f11 = Toggle fullscreen
bind right = player1 RIGHT
bind left = player1 LEFT
bind down = player1 DOWN
bind up = player1 UP
bind eject = CD Change button
bind reset = RESET button
binddev = sdl:Sony Interactive Entertainment Controller
bind escape = Enter Menu
bind backspace = Fast Forward
bind f1 = Save State
bind f2 = Load State
bind f3 = Prev Save Slot
bind f4 = Next Save Slot
bind f5 = Toggle Frameskip
bind f6 = Take Screenshot
bind f7 = Show/Hide FPS
bind f8 = Switch Renderer
bind f9 = CD Change button
bind f10 = RESET button
bind f11 = Toggle fullscreen
bind right = player1 RIGHT
bind left = player1 LEFT
bind down = player1 DOWN
bind up = player1 UP
bind \\xF0 = player1 TRIANGLE
bind \\xF1 = player1 CIRCLE
bind \\xF2 = player1 CROSS
bind \\xF3 = player1 SQUARE
bind \\xF4 = player1 L2
bind \\xF5 = player1 R2
bind \\xF6 = player1 L1
bind \\xF7 = player1 R1
bind \\xF8 = player1 SELECT
bind \\xF9 = player1 START
bind eject = CD Change button
bind reset = RESET button
binddev = sdl:Sony Interactive Entertainment Controller [1]
bind escape = Enter Menu
bind backspace = Fast Forward
bind f1 = Save State
bind f2 = Load State
bind f3 = Prev Save Slot
bind f4 = Next Save Slot
bind f5 = Toggle Frameskip
bind f6 = Take Screenshot
bind f7 = Show/Hide FPS
bind f8 = Switch Renderer
bind f9 = CD Change button
bind f10 = RESET button
bind f11 = Toggle fullscreen
bind right = player2 RIGHT
bind left = player2 LEFT
bind down = player2 DOWN
bind up = player2 UP
bind \\xF0 = player2 TRIANGLE
bind \\xF1 = player2 CIRCLE
bind \\xF2 = player2 CROSS
bind \\xF3 = player2 SQUARE
bind \\xF4 = player2 L2
bind \\xF5 = player2 R2
bind \\xF6 = player2 L1
bind \\xF7 = player2 R1
bind \\xF8 = player2 SELECT
bind \\xF9 = player2 START
bind eject = CD Change button
bind reset = RESET button
binddev = sdl:Sony SCPH-1000R
bind escape = Enter Menu
bind backspace = Fast Forward
bind f1 = Save State
bind f2 = Load State
bind f3 = Prev Save Slot
bind f4 = Next Save Slot
bind f5 = Toggle Frameskip
bind f6 = Take Screenshot
bind f7 = Show/Hide FPS
bind f8 = Switch Renderer
bind f9 = CD Change button
bind f10 = RESET button
bind f11 = Toggle fullscreen
bind right = player1 RIGHT
bind left = player1 LEFT
bind down = player1 DOWN
bind up = player1 UP
bind \\xF0 = player1 TRIANGLE
bind \\xF1 = player1 CIRCLE
bind \\xF2 = player1 CROSS
bind \\xF3 = player1 SQUARE
bind \\xF4 = player1 L2
bind \\xF5 = player1 R2
bind \\xF6 = player1 L1
bind \\xF7 = player1 R1
bind \\xF8 = player1 SELECT
bind \\xF9 = player1 START
bind eject = CD Change button
bind reset = RESET button
binddev = sdl:Sony SCPH-1000R [1]
bind escape = Enter Menu
bind backspace = Fast Forward
bind f1 = Save State
bind f2 = Load State
bind f3 = Prev Save Slot
bind f4 = Next Save Slot
bind f5 = Toggle Frameskip
bind f6 = Take Screenshot
bind f7 = Show/Hide FPS
bind f8 = Switch Renderer
bind f9 = CD Change button
bind f10 = RESET button
bind f11 = Toggle fullscreen
bind right = player2 RIGHT
bind left = player2 LEFT
bind down = player2 DOWN
bind up = player2 UP
bind \\xF0 = player2 TRIANGLE
bind \\xF1 = player2 CIRCLE
bind \\xF2 = player2 CROSS
bind \\xF3 = player2 SQUARE
bind \\xF4 = player2 L2
bind \\xF5 = player2 R2
bind \\xF6 = player2 L1
bind \\xF7 = player2 R1
bind \\xF8 = player2 SELECT
bind \\xF9 = player2 START
bind eject = CD Change button
bind reset = RESET button
binddev = sdl:iBUFFALO BSGP1204 Series
bind escape = Enter Menu
bind backspace = Fast Forward
bind f1 = Save State
bind f2 = Load State
bind f3 = Prev Save Slot
bind f4 = Next Save Slot
bind f5 = Toggle Frameskip
bind f6 = Take Screenshot
bind f7 = Show/Hide FPS
bind f8 = Switch Renderer
bind f9 = CD Change button
bind f10 = RESET button
bind f11 = Toggle fullscreen
bind right = player1 RIGHT
bind left = player1 LEFT
bind down = player1 DOWN
bind up = player1 UP
bind \\xF0 = player1 TRIANGLE
bind \\xF1 = player1 CIRCLE
bind \\xF2 = player1 CROSS
bind \\xF3 = player1 SQUARE
bind \\xF4 = player1 L2
bind \\xF5 = player1 R2
bind \\xF6 = player1 L1
bind \\xF7 = player1 R1
bind \\xF8 = player1 SELECT
bind \\xF9 = player1 START
bind eject = CD Change button
bind reset = RESET button
binddev = sdl:iBUFFALO BSGP1204 Series [1]
bind escape = Enter Menu
bind backspace = Fast Forward
bind f1 = Save State
bind f2 = Load State
bind f3 = Prev Save Slot
bind f4 = Next Save Slot
bind f5 = Toggle Frameskip
bind f6 = Take Screenshot
bind f7 = Show/Hide FPS
bind f8 = Switch Renderer
bind f9 = CD Change button
bind f10 = RESET button
bind f11 = Toggle fullscreen
bind right = player2 RIGHT
bind left = player2 LEFT
bind down = player2 DOWN
bind up = player2 UP
bind \\xF0 = player2 TRIANGLE
bind \\xF1 = player2 CIRCLE
bind \\xF2 = player2 CROSS
bind \\xF3 = player2 SQUARE
bind \\xF4 = player2 L2
bind \\xF5 = player2 R2
bind \\xF6 = player2 L1
bind \\xF7 = player2 R1
bind \\xF8 = player2 SELECT
bind \\xF9 = player2 START
bind eject = CD Change button
bind reset = RESET button
'''
PNG_TMP = 'iVBORw0KGgoAAAANSUhEUgAAAOIAAADiBAMAAAChPgbkAAAAIVBMVEXMzMyWlpaxsbGcnJy3t7ejo6PFxcW+vr6qqqq5ubmgoKAgDAxOAAAACXBIWXMAAA7EAAAOxAGVKw4bAAABcklEQVR4nO3TTWvbQBSF4TOxZHk5FzcJZGXq/gBTJ3ayM0pNutSm7tamuN0KikmXJsSkPzt3/BUKWamrhPfBWEhzmINmNBIAAAAAAAAAAAAAAAAAAAAAAMBb1P+s1VX9pNKs6g5r6a/C8MbszC/jIHXWKeKDUdGD/qR7rUO2iWy2vBsX41JPUYrFQBoq6Lf8LujW528NPDJJgzr3oD+Jnd4h20Ret1cTTZcapFnaUcXG32Oxa1z4/H++e6TeNp56MDW2D9lG0lvM9SP/WaVZskonZS9oumvs++inj/6Xbs26HkyNivts08bgE52UE7Oe2UStX1WwD9tGS2s4WqVGH4yyY+M+20heFxtfrGIz3+/Nws6O++i/ttmyLtb/rGpR/c8+ZrP83j8IfdN20qhSj8GbDo1Zr/NlltevfDlquI/qX6bToYfdARhppq9Brfm+0S7m2dojL6fDznenI2UBAAAAAAAAAAAAAAAAAAAAAMD79AyLIjRAm3AhLAAAAABJRU5ErkJggg=='

DEFAULT_GAME_TITLE = ''
DEFAULT_GAME_PUBLISHER = 'Unknown'
DEFAULT_GAME_NO_OF_PLAYERS = 1
DEFAULT_GAME_YEAR = 1994

root_window = tkinter.Tk()
root_window.title(WINDOW_TITLE)
root_window.geometry('480x700')

games_listbox = tkinter.Listbox(root_window)
games_listbox.pack(fill=tkinter.BOTH, expand=True)

log_text = tkinter.Text(root_window, height=8)
log_text.pack(fill=tkinter.X)

select_dir_button = tkinter.Button(root_window, text='Select directory')
select_dir_button.pack(fill=tkinter.X)

add_game_button = tkinter.Button(root_window, text='Add game from directory')
add_game_button.pack(fill=tkinter.X)

add_game_from_arch_button = tkinter.Button(root_window, text='Add game from archive (7z, zip, rar, ...)')
add_game_from_arch_button.pack(fill=tkinter.X)

edit_game_button = tkinter.Button(root_window, text='Edit game')
edit_game_button.pack(fill=tkinter.X)

delete_game_button = tkinter.Button(root_window, text='Remove game (move to ' + GAMES_DELETED_DIR + ')')
delete_game_button.pack(fill=tkinter.X)

delete_game_permanently_button = tkinter.Button(root_window, text='Remove game (delete permanently)')
delete_game_permanently_button.pack(fill=tkinter.X)

sort_games_button = tkinter.Button(root_window, text='Sort games by title')
sort_games_button.pack(fill=tkinter.X)

move_game_up_button = tkinter.Button(root_window, text='Move game UP')
move_game_up_button.pack(fill=tkinter.X)

move_game_down_button = tkinter.Button(root_window, text='Move game DOWN')
move_game_down_button.pack(fill=tkinter.X)

apply_button = tkinter.Button(root_window, text='Apply changes')
apply_button.pack(fill=tkinter.X)

homepage_button = tkinter.Button(root_window, text='Homepage')
homepage_button.pack(fill=tkinter.X)

exit_button = tkinter.Button(root_window, text='Exit')
exit_button.pack(fill=tkinter.X)

status_bar = tkinter.Label(root_window, bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W)
status_bar.pack(side=tkinter.BOTTOM, fill=tkinter.X)

progress_bar = tkinter.ttk.Progressbar(root_window, orient=tkinter.HORIZONTAL, length=100, mode='determinate')
progress_bar.pack(fill=tkinter.X)
progress_bar['value'] = 0


def log(s):
    log_text.insert(tkinter.END, str(s) + '\n')
    log_text.see(tkinter.END)


def parse_game_ini(game_ini_path):
    parsed = {}

    with open(game_ini_path) as f:
        for line in f.readlines():
            line = line.strip()

            if '=' not in line:
                continue

            parts = line.split('=')
            parsed[parts[0]] = parts[1]

    return parsed


def file_get_crc32(fileName):
    prev = 0
    for eachLine in open(fileName,"rb"):
        prev = zlib.crc32(eachLine, prev)
    return "%X"%(prev & 0xFFFFFFFF)


def load_games_list(directory):
    global games_list

    games_list = []

    games_directory = os.path.join(directory, 'Games')

    if not os.path.exists(games_directory):
        log('Creating ' + games_directory)
        os.makedirs(games_directory)

    indexes = sorted([int(name) for name in os.listdir(games_directory) if name.isnumeric()])

    for iindex in indexes:
        gamedata_directory = os.path.join(games_directory, str(iindex), 'GameData')

        game_ini = os.path.join(gamedata_directory, 'Game.ini')
        pcsx_cfg = os.path.join(gamedata_directory, 'pcsx.cfg')

        if not os.path.exists(game_ini) or not os.path.exists(pcsx_cfg):
            log(game_ini + ' or ' + pcsx_cfg + ' does not exists, stopping')

            games_list = []
            return

        parsed_game_data = parse_game_ini(game_ini)
        parsed_game_data['_directory'] = os.path.join(games_directory, str(iindex))
        parsed_game_data['_status'] = ''
        parsed_game_data['_png_disc1_pathname'] = os.path.join(gamedata_directory, parsed_game_data['Discs'].split(',')[0] + '.png')
        parsed_game_data['_png_disc1_crc32'] = ''

        if os.path.exists(parsed_game_data['_png_disc1_pathname']):
            parsed_game_data['_png_disc1_crc32'] = file_get_crc32(parsed_game_data['_png_disc1_pathname'])
        else:
            parsed_game_data['_png_disc1_pathname'] = ''

        games_list.append(parsed_game_data)


def render_games_list():
    games_listbox.delete(0, tkinter.END)

    for igame_ini in games_list:
        if igame_ini['_status'] == 'deleted':
            row_title = igame_ini['Title'] + ' (deleted)'
        elif igame_ini['_status'] == 'moved':
            row_title = igame_ini['Title'] + ' (moved)'
        else:
            row_title = igame_ini['Title']

        games_listbox.insert(tkinter.END, row_title)


def on_select_dir_button_click(e):
    global current_directory

    try:
        directory = tkinter.filedialog.askdirectory(initialdir='/home/sng/psc')
        if directory:
            log('Loading games from ' + directory)

            current_directory = directory

            load_games_list(directory)

            games_deleted_dir = os.path.join(current_directory, GAMES_DELETED_DIR)
            if not os.path.exists(games_deleted_dir):
                log('Creating ' + games_deleted_dir)

                os.mkdir(games_deleted_dir)

            log('Loaded ' + str(len(games_list)) + ' games')

            render_games_list()
    except Exception as x:
        traceback.print_exc()
        log('Error: ' + str(x))

        current_directory = None


def show_select_directory_msg():
    log('Directory not selected. Use Select directory first')


def games_listbox_set_text(index, text):
    games_listbox.delete(index)
    games_listbox.insert(index, text)


def move_game(up):
    global games_list

    selected_game_index = games_listbox.curselection()
    if not selected_game_index:
        return

    selected_game_index = selected_game_index[0]
    if selected_game_index == 0 and up:
        # want to move first game up?
        return
    if selected_game_index + 1 == games_listbox.size() and not up:
        # want to move last game down?
        return

    offset = -1 if up else 1

    # move on listbox
    games_listbox.delete(selected_game_index)
    games_listbox.insert(selected_game_index + offset, games_list[selected_game_index]['Title'] + ' (moved)')

    games_listbox.selection_set(selected_game_index + offset)

    # move in memory
    game_data = games_list[selected_game_index]
    game_data['_status'] = 'moved'

    del games_list[selected_game_index]
    games_list.insert(selected_game_index + offset, game_data)


def on_move_game_up_button_click(e):
    if not current_directory:
        show_select_directory_msg()
        return

    move_game(True)


def on_move_game_down_button_click(e):
    if not current_directory:
        show_select_directory_msg()
        return

    move_game(False)


def on_sort_games_button_click(e):
    global games_list

    if not current_directory:
        show_select_directory_msg()
        return

    # remove "moved" mark, because we are sorting all of them
    for igame_data in games_list:
        if igame_data['_status'] == 'moved':
            igame_data['_status'] = ''

    games_list = sorted(games_list, key=itemgetter('Title'))
    render_games_list()


def deltree(target):
    if not os.path.exists(target):
        return

    for d in os.listdir(target):
        try:
            deltree(target + os.path.sep + d)
        except OSError:
            os.remove(target + os.path.sep + d)

    os.rmdir(target)


def write_games_list():
    global games_list

    # delete games marked for permanently deletion
    for igame_data in games_list.copy():
        if igame_data['_status'] == 'deleted_permanently':
            log('Removing permanently ' + igame_data['Title'])

            deltree(igame_data['_directory'])
            games_list.remove(igame_data)

    # rename all games to _index_
    for index in range(len(games_list)):
        igame_data = games_list[index]

        new_directory = os.path.join(os.path.dirname(igame_data['_directory']), '_' + str(index) + '_')
        os.rename(igame_data['_directory'], new_directory)

        igame_data['_directory'] = new_directory

    # rewrite games
    games_deleted_dir = os.path.join(current_directory, GAMES_DELETED_DIR)

    index = 1
    for igame_data in games_list:
        if igame_data['_status'] == 'deleted':
            log('Removing (moving) ' + igame_data['Title'])

            os.rename(igame_data['_directory'], os.path.join(games_deleted_dir, os.path.basename(igame_data['_directory'])))
            continue
        elif igame_data['_status'] == 'changed':
            # rewrite Game.ini
            game_ini_path = os.path.join(igame_data['_directory'], 'GameData', 'Game.ini')

            with open(game_ini_path, 'w+') as f:
                game_ini_data = GAME_INI_TMP.format(
                    discs = igame_data['Discs'],
                    title = igame_data['Title'],
                    publisher = igame_data['Publisher'],
                    players = igame_data['Players'],
                    year = igame_data['Year']
                )
                f.write(game_ini_data)

            # prepare new cover art
            if igame_data['_png_disc1_pathname']:
                new_crc32 = file_get_crc32(igame_data['_png_disc1_pathname'])
                if new_crc32 != igame_data['_png_disc1_crc32']:
                    image = Image.open(igame_data['_png_disc1_pathname'])
                    if image.width != COVER_ART_WIDTH or image.height != COVER_ART_HEIGHT:
                        image = ImageOps.fit(image, (COVER_ART_WIDTH, COVER_ART_HEIGHT), Image.ANTIALIAS)

                    gamedata_directory = os.path.join(igame_data['_directory'], 'GameData')
                    igame_data['_png_disc1_pathname'] = os.path.join(gamedata_directory, igame_data['Discs'].split(',')[0] + '.png')
                    image.save(igame_data['_png_disc1_pathname'])

                    igame_data['_png_disc1_crc32'] = file_get_crc32(igame_data['_png_disc1_pathname'])

        new_directory = os.path.join(os.path.dirname(igame_data['_directory']), str(index))
        os.rename(igame_data['_directory'], new_directory)

        igame_data['_directory'] = new_directory

        index += 1


def sync_all():
    if hasattr(os, 'sync'):
        log('Syncing disk (force write of everything to disk)')
        os.sync()


def run_bleem_sync():
    system_name = platform.system().lower()
    exe_pathname = None

    os.chdir(os.path.join(current_directory, 'BleemSync'))

    if system_name == 'linux':
        exe_pathname = os.path.join(current_directory, 'BleemSync', 'BleemSync')
    elif system_name == 'windows':
        exe_pathname = os.path.join(current_directory, 'BleemSync', 'BleemSync.exe')
    else:
        raise NotImplementedError('Not implemented for ' + system_name)

    log('Running ' + exe_pathname)

    bs_process = subprocess.Popen([exe_pathname], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    bs_stdout, bs_stderr = bs_process.communicate(input=str.encode('\n'))
    output = str(bs_stdout.decode().strip() + '\n' + bs_stderr.decode().strip()).strip()
    exit_code = bs_process.returncode

    log('=== BLEEMSYNC OUTPUT START ===')
    log(output)
    log('=== BLEEMSYNC OUTPUT END ===')
    log('=== BLEEMSYNC EXIT CODE: {code} ==='.format(code = exit_code))

    sync_all()


def bgt_apply_changes():
    try:
        if not current_directory:
            show_select_directory_msg()
            return

        enable_all_buttons(False)

        log('Applying changes')

        write_games_list()

        log('Running BleemSync')
        run_bleem_sync()

        load_games_list(current_directory)
        render_games_list()

        log('Done')
    except Exception as x:
        traceback.print_exc()
        log('Error: ' + str(x))
    finally:
        enable_all_buttons(True)


def set_progress_bar(current_counter, len_operations):
    if not current_counter and not len_operations:
        progress_bar['value'] = 0
        return

    progress_bar['value'] = current_counter / len_operations * 100


def file_extract_strings(filename, min=4):
    with open(filename, errors="ignore") as f:  # Python 3.x
    # with open(filename, "rb") as f:           # Python 2.x
        result = ""
        for c in f.read():
            if c in string.printable:
                result += c
                continue
            if len(result) >= min:
                yield result
            result = ""
        if len(result) >= min:  # catch result at EOF
            yield result


def bin_file_find_disc_id(bin_path):
    disc_id_sign1 = 'BOOT=cdrom:\\'
    disc_id_sign2 = 'BOOT = cdrom:\\'
    disc_id_sign3 = 'BOOT  = cdrom:\\'
    cdrom_sign = 'cdrom:\\'

    strings = list(file_extract_strings(bin_path, 50))
    for istr in strings:
        if istr.find(disc_id_sign1) != -1 or istr.find(disc_id_sign2) != -1 or istr.find(disc_id_sign3) != -1:
            istr_lines = [line.strip() for line in istr.strip().split('\n')]

            for line in istr_lines:
                if line.startswith(disc_id_sign1) or line.startswith(disc_id_sign2) or line.startswith(disc_id_sign3):
                    cdrom_pos = line.find(cdrom_sign)
                    if cdrom_pos != -1:
                        line = line[cdrom_pos + len(cdrom_sign):]

                        semicolon_pos = line.find(';')
                        if semicolon_pos != -1:
                            line = line[0:semicolon_pos]
                        
                        line = line.replace('.', '').replace('_', '-')
                        return line

    return None


def bgt_unpack_file(pathname, target_dir, callback):
    try:
        if not current_directory:
            show_select_directory_msg()
            return

        enable_all_buttons(False)

        if os.path.exists(target_dir):
            deltree(target_dir)

        os.makedirs(target_dir)

        log('Unpacking ' + pathname + ' to ' + target_dir)

        pyunpack.Archive(pathname).extractall(target_dir)

        sync_all()

        callback(pathname, target_dir)
    except Exception as x:
        traceback.print_exc()
        log('Error: ' + str(x))

        set_progress_bar(0, 0)
    finally:
        enable_all_buttons(True)


def bgt_add_game(directory, new_game_data, delete_src_game_dir):
    new_game_directory = None

    try:
        if not current_directory:
            show_select_directory_msg()
            return

        enable_all_buttons(False)

        log('Adding game from ' + directory)

        new_game_id = len(games_list) + 1
        new_game_directory = os.path.join(current_directory, 'Games', str(new_game_id))
        new_gamedata_directory = os.path.join(new_game_directory, 'GameData')

        log('Creating ' + new_gamedata_directory)
        if not os.path.exists(new_gamedata_directory):
            os.makedirs(new_gamedata_directory)

        log('Copying game files')

        set_progress_bar(0, 0)

        files = os.listdir(directory)
        len_operations = len(files) + 4
        counter = 0

        for ifilename in files:
            src_file = os.path.join(directory, ifilename)

            log('Copying ' + src_file)
            shutil.copyfile(src_file, os.path.join(new_gamedata_directory, ifilename))

            counter += 1
            set_progress_bar(counter, len_operations)

        sync_all()

        counter += 1
        set_progress_bar(counter, len_operations)

        game_ini_path = os.path.join(new_gamedata_directory, 'Game.ini')
        pcsx_cfg_path = os.path.join(new_gamedata_directory, 'pcsx.cfg')

        if not os.path.exists(game_ini_path):
            log('Searching for disc ID')

            disc_id = None
            disc_id_bin = None

            bin_files = sorted([ifilename for ifilename in os.listdir(new_gamedata_directory) if ifilename.endswith('.bin')])
            cue_files = sorted([ifilename for ifilename in os.listdir(new_gamedata_directory) if ifilename.endswith('.cue')])

            if not bin_files:
                log('No .bin files, game cannot be added, reverting')

                deltree(new_game_directory)
                return

            cue_file = cue_files[0] if cue_files else None
            first_bin_path = os.path.join(new_gamedata_directory, bin_files[0])

            log('Searching in ' + first_bin_path)
            disc_id = bin_file_find_disc_id(first_bin_path)
            disc_id_bin = bin_files[0]

            # disc_id = 'SLUS-01260'

            # for ifilename in bin_files:
            #     bin_path = os.path.join(new_game_directory, ifilename)

            #     log('Searching in ' + bin_path)

            #     disc_id = bin_file_find_disc_id(bin_path)
            #     # disc_id = 'SLES-00556'
            #     if disc_id:
            #         disc_id_bin = ifilename
            #         break

            if not disc_id:
                log('Disc ID not found, game cannot be added, reverting')

                deltree(new_game_directory)
                return

            log('Disc ID ' + disc_id + ' found in ' + disc_id_bin)

            new_cue_file_path = os.path.join(new_gamedata_directory, disc_id + '.cue')

            bin_files.remove(disc_id_bin)

            old_bin_path = os.path.join(new_gamedata_directory, disc_id_bin)
            new_bin_path = os.path.join(new_gamedata_directory, disc_id + '.bin')

            log('Renaming ' + old_bin_path + ' to ' + new_bin_path)
            os.rename(old_bin_path, new_bin_path)

            if cue_file:
                cue_file_path = os.path.join(new_gamedata_directory, cue_file)
        
                log('Patching ' + cue_file_path)

                with open(cue_file_path, 'r+') as f:
                    cue_data = f.read()

                    f.seek(0)
                    f.truncate(0)

                    f.write(cue_data.replace(disc_id_bin, disc_id + '.bin'))
                
                log('Renaming ' + cue_file_path + ' to ' + new_cue_file_path)
                os.rename(cue_file_path, new_cue_file_path)
            else:
                log('Creating ' + new_cue_file_path)

                with open(new_cue_file_path, 'w+') as f:
                    f.write('FILE "{bin_filename}" BINARY\n'.format(bin_filename=disc_id + '.bin'))
                    f.write('  TRACK 01 MODE1/2352\n')
                    f.write('    INDEX 01 00:00:00\n')

                    counter = 2
                    for ifilename in bin_files:
                        f.write('FILE "{bin_filename}" BINARY\n'.format(bin_filename=ifilename))
                        f.write('  TRACK {counter:02} AUDIO\n'.format(counter=counter))
                        f.write('    INDEX 00 00:00:00\n')
                        f.write('    INDEX 01 00:02:00\n')

                        counter += 1

            log('Creating ' + game_ini_path)

            with open(game_ini_path, 'w+') as f:
                game_ini_data = GAME_INI_TMP.format(
                    discs = disc_id,
                    title = new_game_data['Title'],
                    publisher = new_game_data['Publisher'],
                    players = new_game_data['Players'],
                    year = new_game_data['Year']
                )
                f.write(game_ini_data)

            png_path = os.path.join(new_gamedata_directory, disc_id + '.png')
            log('Creating ' + png_path)

            with open(png_path, 'wb') as f:
                f.write(base64.b64decode(PNG_TMP))

        if not os.path.exists(pcsx_cfg_path):
            log('Creating ' + pcsx_cfg_path)

            with open(pcsx_cfg_path, 'w+') as f:
                f.write(PCSX_CFG_TMP)

        counter += 1
        set_progress_bar(counter, len_operations)

        sync_all()

        counter += 1
        set_progress_bar(counter, len_operations)

        log('Running BleemSync')
        run_bleem_sync()

        counter += 1
        set_progress_bar(counter, len_operations)
    except Exception as x:
        traceback.print_exc()
        log('Error: ' + str(x))

        if new_game_directory:
            log('Reverting')
            deltree(new_game_directory)

        set_progress_bar(0, 0)
    finally:
        if delete_src_game_dir:
            log('Deleting ' + directory)
            deltree(directory)

        log('Reloading games')
        load_games_list(current_directory)
        render_games_list()

        set_progress_bar(100, 100)

        log('Done')

        enable_all_buttons(True)


def on_apply_button_click(e):
    global background_thread_states

    if not current_directory:
        show_select_directory_msg()
        return

    if background_thread_states:
        return

    enable_all_buttons(False)

    background_thread_states.append({
        'state': BGT_STATE_APPLY_CHANGES,
        'data': {}
    })


def select_next_to_game(game_index):
    if game_index + 1 == games_listbox.size():
        games_listbox.selection_set(0)
    elif game_index + 1 < games_listbox.size():
        games_listbox.selection_set(game_index + 1)


def on_delete_game_button_click(e):
    global games_list

    if not current_directory:
        show_select_directory_msg()
        return

    selected_game_index = games_listbox.curselection()
    if not selected_game_index:
        return

    selected_game_index = selected_game_index[0]

    # mark on listbox
    games_listbox_set_text(selected_game_index, games_list[selected_game_index]['Title'] + ' (deleted)')

    # mark as deleted
    games_list[selected_game_index]['_status'] = 'deleted'

    # select next game, or first
    select_next_to_game(selected_game_index)

    log('Game ' + games_list[selected_game_index]['Title'] + ' marked for deletion')


def on_delete_game_permanently_button_click(e):
    global games_list

    if not current_directory:
        show_select_directory_msg()
        return

    selected_game_index = games_listbox.curselection()
    if not selected_game_index:
        return

    selected_game_index = selected_game_index[0]

    # mark on listbox
    games_listbox_set_text(selected_game_index, games_list[selected_game_index]['Title'] + ' (deleted permanently)')

    # mark as deleted
    games_list[selected_game_index]['_status'] = 'deleted_permanently'

    # select next game, or first
    select_next_to_game(selected_game_index)

    log('Game ' + games_list[selected_game_index]['Title'] + ' marked for deletion permanently')


def game_edit_window(game_name=None, publisher=None, year=None, no_of_players=None, _png_disc1_pathname=None):
    global root_window

    if not game_name:
        game_name = DEFAULT_GAME_TITLE
    if not publisher:
        publisher = DEFAULT_GAME_PUBLISHER
    if not year:
        year = DEFAULT_GAME_YEAR
    if not no_of_players:
        no_of_players = DEFAULT_GAME_NO_OF_PLAYERS
    if not _png_disc1_pathname:
        _png_disc1_pathname = ''

    window = tkinter.Toplevel(root_window)

    window.wait_visibility()
    window.grab_set()
    window.update()

    window.title('Enter game data')

    tkinter.Label(window, text='Title:').pack(fill=tkinter.X)
    title_var = tkinter.StringVar(value=game_name)
    tkinter.Entry(window, textvariable=title_var).pack(fill=tkinter.X)

    tkinter.Label(window, text='Publisher:').pack(fill=tkinter.X)
    publisher_var = tkinter.StringVar(value=publisher)
    tkinter.Entry(window, textvariable=publisher_var).pack(fill=tkinter.X)

    tkinter.Label(window, text='Number of players:').pack(fill=tkinter.X)
    players_var = tkinter.IntVar(value=no_of_players)
    tkinter.Entry(window, textvariable=players_var).pack(fill=tkinter.X)

    tkinter.Label(window, text='Year:').pack(fill=tkinter.X)
    year_var = tkinter.IntVar(value=year)
    tkinter.Entry(window, textvariable=year_var).pack(fill=tkinter.X)

    tkinter.Label(window, text='Cover art (click to change):').pack(fill=tkinter.X)

    if _png_disc1_pathname:
        try:
            cover_art_image = ImageOps.fit(Image.open(_png_disc1_pathname), (COVER_ART_WIDTH, COVER_ART_HEIGHT), Image.ANTIALIAS)
        except Exception as x:
            traceback.print_exc()
            log('Error: ' + str(x))

            cover_art_image = Image.open(io.BytesIO(base64.b64decode(PNG_TMP)))
    else:
        cover_art_image = Image.open(io.BytesIO(base64.b64decode(PNG_TMP)))

    cover_art_tk_image = ImageTk.PhotoImage(cover_art_image)

    cover_art_label = tkinter.Label(window, text='', image=cover_art_tk_image, cursor='hand1', width=COVER_ART_WIDTH, height=COVER_ART_HEIGHT)
    cover_art_label.pack(fill=tkinter.X)

    tkinter.ttk.Separator(window).pack(fill=tkinter.X)

    can_return_game = False

    def on_ok_button_click(e):
        nonlocal can_return_game

        if not title_var.get().strip():
            tkinter.messagebox.showwarning(WINDOW_TITLE, 'Please enter game\'s Title')
            return
        if not publisher_var.get().strip():
            tkinter.messagebox.showwarning(WINDOW_TITLE, 'Please enter game\'s Publisher')
            return
        if players_var.get() < 1:
            tkinter.messagebox.showwarning(WINDOW_TITLE, 'Number of players must be > 1')
            return
        if year_var.get() < 1994:
            tkinter.messagebox.showwarning(WINDOW_TITLE, 'Year must be >= 1994')
            return

        can_return_game = True

        window.destroy()

    def on_cover_art_label_click(e):
        nonlocal cover_art_tk_image
        nonlocal cover_art_label
        nonlocal _png_disc1_pathname

        image_pathname = tkinter.filedialog.askopenfile(initialdir='~/Downloads', filetypes = (("png files","*.png"), ("jpg files","*.jpg"), ("all files","*.*")))
        if image_pathname:
            _png_disc1_pathname = image_pathname.name

            try:
                cover_art_image = ImageOps.fit(Image.open(_png_disc1_pathname), (COVER_ART_WIDTH, COVER_ART_HEIGHT), Image.ANTIALIAS)
            except Exception as x:
                traceback.print_exc()
                log('Error: ' + str(x))
                
                cover_art_image = Image.open(io.BytesIO(base64.b64decode(PNG_TMP)))

            cover_art_tk_image = ImageTk.PhotoImage(cover_art_image)

            cover_art_label.configure(image=cover_art_tk_image)
            cover_art_label.image = cover_art_tk_image

    ok_button = tkinter.Button(window, text='OK')
    ok_button.pack(fill=tkinter.X)
    ok_button.bind('<ButtonRelease-1>', on_ok_button_click)

    cover_art_label.bind('<ButtonRelease-1>', on_cover_art_label_click)

    root_window.wait_window(window)

    if not can_return_game:
        return None

    return {
        'Title': title_var.get().strip(),
        'Publisher': publisher_var.get().strip(),
        'Players': players_var.get(),
        'Year': year_var.get(),
        '_png_disc1_pathname': _png_disc1_pathname
    }


def detect_game_name(directory):
    bin_files = sorted([ifilename for ifilename in os.listdir(directory) if ifilename.endswith('.bin')])

    remove_brackets_pattern = r'\(.*?\)'
    filtered = []

    for ibin_file in bin_files:
        # remove brackets and extension
        cleaned_file = os.path.splitext(re.sub(remove_brackets_pattern, '', ibin_file).strip())[0].strip()

        if cleaned_file not in filtered:
            filtered.append(cleaned_file)

    if not filtered:
        return None
    
    return filtered[0]


def game_exists_by_name(game_name):
    for igame_data in games_list:
        if igame_data['Title'] == game_name:
            return True

    return False


def on_unpack_done(pathname, target_dir):
    global on_add_game_button_click_user_data

    on_add_game_button_click_user_data = {
        'directory': target_dir,
        'force': True,
        'delete_src_game_dir': True
    }
    add_game_button.event_generate('<ButtonRelease-1>', when='tail')


def on_add_game_from_arch_button_click(e):
    global background_thread_states

    if not current_directory:
        show_select_directory_msg()
        return

    if background_thread_states:
        return

    file_data = tkinter.filedialog.askopenfile(initialdir='~/Downloads', filetypes = (("7z files","*.7z"), ("zip files","*.zip"), ("rar files","*.rar"), ("all files","*.*")))
    if file_data:
        enable_all_buttons(False)

        background_thread_states.append({
            'state': BGT_STATE_UNPACK_FILE,
            'data': {
                'pathname': file_data.name,
                'target_dir': os.path.join(tempfile.gettempdir(), os.path.splitext(os.path.basename(file_data.name))[0]),
                'callback': on_unpack_done
            }
        })


def on_add_game_button_click(e):
    global on_add_game_button_click_user_data
    global background_thread_states

    directory = None
    force = False
    delete_src_game_dir = False

    if on_add_game_button_click_user_data:
        directory = on_add_game_button_click_user_data['directory']
        force = on_add_game_button_click_user_data['force']
        delete_src_game_dir = on_add_game_button_click_user_data['delete_src_game_dir']

        on_add_game_button_click_user_data = {}

    if not current_directory:
        show_select_directory_msg()
        return

    if background_thread_states and not force:
        return

    if not directory:
        directory = tkinter.filedialog.askdirectory(initialdir='~/Downloads/mt')

    if directory:
        enable_all_buttons(False)

        if not os.path.exists(os.path.join(directory, 'Game.ini')):
            game_name = detect_game_name(directory)
            if game_name:
                log('Detected game name: ' + game_name)

            if not game_name:
                new_game_data = game_edit_window(game_name)
            else:
                new_game_data = {
                    'Title': game_name,
                    'Publisher': DEFAULT_GAME_PUBLISHER,
                    'Players': DEFAULT_GAME_NO_OF_PLAYERS,
                    'Year': DEFAULT_GAME_YEAR
                }

            if not new_game_data:
                # canceled
                if delete_src_game_dir and os.path.exists(directory):
                    log('Deleting ' + directory)
                    deltree(directory)

                enable_all_buttons(True)
                return

            if game_exists_by_name(game_name):
                log('Game with such name already exists.')

                if delete_src_game_dir and os.path.exists(directory):
                    log('Deleting ' + directory)
                    deltree(directory)

                enable_all_buttons(True)
                return
        else:
            new_game_data = None

        background_thread_states.append({
            'state': BGT_STATE_ADD_GAME,
            'data': {
                'directory': directory,
                'game_data': new_game_data,
                'delete_src_game_dir': delete_src_game_dir
            }
        })


def enable_all_buttons(enable):
    global buttons_enabled

    new_state = tkinter.NORMAL if enable else tkinter.DISABLED

    select_dir_button['state'] = new_state
    exit_button['state'] = new_state
    move_game_up_button['state'] = new_state
    move_game_down_button['state'] = new_state
    sort_games_button['state'] = new_state
    apply_button['state'] = new_state
    add_game_button['state'] = new_state
    add_game_from_arch_button['state'] = new_state
    delete_game_button['state'] = new_state
    delete_game_permanently_button['state'] = new_state
    edit_game_button['state'] = new_state

    buttons_enabled = new_state


def on_root_window_exit():
    global background_thread_run

    if buttons_enabled:
        background_thread_run = False
        root_window.destroy()


def on_exit_button_click(e):
    on_root_window_exit()


def on_edit_game_button_click(e):
    global games_list

    if not current_directory:
        show_select_directory_msg()
        return

    selected_game_index = games_listbox.curselection()
    if not selected_game_index:
        return

    selected_game_index = selected_game_index[0]
    game_data = games_list[selected_game_index]

    new_game_data = game_edit_window(game_data['Title'], game_data['Publisher'], game_data['Year'], game_data['Players'], game_data['_png_disc1_pathname'])
    if new_game_data:
        games_list[selected_game_index]['Title'] = new_game_data['Title']
        games_list[selected_game_index]['Publisher'] = new_game_data['Publisher']
        games_list[selected_game_index]['Year'] = new_game_data['Year']
        games_list[selected_game_index]['Players'] = new_game_data['Players']

        games_list[selected_game_index]['_png_disc1_pathname'] = new_game_data['_png_disc1_pathname']

        # mark on listbox
        games_listbox_set_text(selected_game_index, games_list[selected_game_index]['Title'] + ' (changed)')

        # mark as changed
        games_list[selected_game_index]['_status'] = 'changed'


def on_listbox_double_click(e):
    selected_game_index = games_listbox.curselection()
    if not selected_game_index:
        return

    edit_game_button.event_generate('<ButtonRelease-1>', when='tail')


def on_homepage_button_click(e):
    webbrowser.open_new(HOMEPAGE_URL)


def background_thread_loop():
    global background_thread_run
    global background_thread_states

    while background_thread_run:
        if background_thread_states:
            new_state_data = background_thread_states.pop(0)

            background_thread_state = new_state_data['state']
            background_thread_data = new_state_data['data']

            if background_thread_state == BGT_STATE_APPLY_CHANGES:
                bgt_apply_changes()
            elif background_thread_state == BGT_STATE_ADD_GAME:
                bgt_add_game(background_thread_data['directory'], background_thread_data['game_data'], background_thread_data['delete_src_game_dir'])
            elif background_thread_state == BGT_STATE_UNPACK_FILE:
                bgt_unpack_file(background_thread_data['pathname'], background_thread_data['target_dir'], background_thread_data['callback'])

        time.sleep(1)


root_window.protocol('WM_DELETE_WINDOW', on_root_window_exit)
select_dir_button.bind('<ButtonRelease-1>', on_select_dir_button_click)
exit_button.bind('<ButtonRelease-1>', on_exit_button_click)
move_game_up_button.bind('<ButtonRelease-1>', on_move_game_up_button_click)
move_game_down_button.bind('<ButtonRelease-1>', on_move_game_down_button_click)
sort_games_button.bind('<ButtonRelease-1>', on_sort_games_button_click)
apply_button.bind('<ButtonRelease-1>', on_apply_button_click)
delete_game_button.bind('<ButtonRelease-1>', on_delete_game_button_click)
delete_game_permanently_button.bind('<ButtonRelease-1>', on_delete_game_permanently_button_click)
add_game_button.bind('<ButtonRelease-1>', on_add_game_button_click)
add_game_from_arch_button.bind('<ButtonRelease-1>', on_add_game_from_arch_button_click)
edit_game_button.bind('<ButtonRelease-1>', on_edit_game_button_click)
games_listbox.bind('<Double-1>', on_listbox_double_click)
homepage_button.bind('<ButtonRelease-1>', on_homepage_button_click)

background_thread = threading.Thread(target=background_thread_loop)
background_thread.start()

root_window.mainloop()
