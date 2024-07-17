# Features
![Blender_Render16-07-2024_06 49 40AM_1384x279x](https://github.com/user-attachments/assets/71c71687-2ea3-4c54-8df1-9b26de5f9d9a)
Once you've set a binding for gpencil.draw_switcher, you can hold it (or press once and release if you enable 'toggle') whenever you're using your standard gpencil.draw bind to switch to whatever brush/material you'd like.

You can also add a TriggerBrush to only trigger the switching if you're on that brush name. Otherwise, it will use the draw mode specified in the keymap, default: Eraser.
# ⚠ Notes (mostly blender faults)
- If you let go of the switcher key without first lifting your pen, the release key will never be given to the addon and the switched-mode will stay until you hit the switcher button again.
  This is because blender suppresses the release notification to the addon while the drawing key is held down. There's nothing I can do to fix it right now.
  If I had added another operator to act like gpencil.draw, it would either always require a pen press to start drawing or never end because gpencil.draw() when cast from an addon never ends if "wait for input" is off.
  This actually happens on the normal gpencil.draw too if you have it activated by button instead of by the eraser signal from your drawing tablet (which blender uses even without a keymap because it gets its own special API and I get nothing.)

- Setting the keybind to an 'eraser key' like shown below probably won't work.

  ![Blender_Render12-07-2024_11 55 23PM_860x157x](https://github.com/user-attachments/assets/7899484e-99e9-4b84-baab-63e04552bb1b)

  The addon listens for any key type and state, so if you can't set the eraser keybind with a physical press, you should probably bind the eraser button on your pen to something different, like a mouse button or key press.

  I use F13 to not absorb limited free key space (F13 is indeed a real thing, they go up to 25 I think.)
  For some reason this isn't a typical key for blender, or at least my wacom tablet doesn't send it as such, and I've never been able to set it by actually pressing an eraser. I always have to select it in keymaps' mouse dropdown menu. I'm on windows, so I don't know if it would be any different on other OSes.
  Good luck if your pen driver/software doesn't have per-app keybindings. I'm sorry.

‌
- If you clear the entry on any field with the X button it may linger and continue switching/acting on trigger as if it was still there. Just manually specify an empty entry (the text box won't be grayed out if you did this right) and that should fix it. You can X it again after if you really want to, it stays fixed after one attempt.

   ![image](https://github.com/user-attachments/assets/b340d50a-f74a-4ffb-9b0d-50e193c1e665) Look for INK Pen. (Case-sensitive)
   ![image](https://github.com/user-attachments/assets/b1c583a3-699d-40f8-9d2e-81e268ac3b7e) Still looking for it, because X was used to clear it.
   ![image](https://github.com/user-attachments/assets/aeb1d16d-0d87-42b2-836e-c78e545d7971) Looking for " ". Not good enough.
   ![image](https://github.com/user-attachments/assets/8be09ee7-c562-485d-80d4-b4f42330f3b9) Won't do any switching, truly empty. The default. Finally.

   Blender moment.

# Installation
Install by going to Preferences > Addons > Install. Install the .zip file directly, you can't install it extracted.
You can delete the original .zip after installing it, blender makes its own copy in its files somewhere. You'll have to redownload to install it again though.
