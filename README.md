# Usage
![br](https://github.com/user-attachments/assets/c368f8d9-4c71-4f79-8098-37417d034d40)
Once you've set a binding for gpencil.draw_switcher, you can hold it whenever you're using your standard gpencil.draw bind to switch to whatever brush/material you'd like.
You can also add a TriggerBrush to only trigger the switching if you're on that brush name. Otherwise, it will use the draw mode specified in the keymap, default: Eraser.
# Notes (mostly blender faults)
- Setting the keybind to an 'eraser key' like shown below probably won't work.

  ![Blender_Render12-07-2024_11 55 23PM_860x157x](https://github.com/user-attachments/assets/7899484e-99e9-4b84-baab-63e04552bb1b)

  The addon listens for any key type and state, so if you can't set the eraser keybind with a physical press, you should probably bind the eraser button on your pen to something different, like a mouse button or key press.

  I use F13 to not absorb limited free key space (F13 is indeed a real thing, they go up to 25 I think.)
  For some reason this isn't a typical key for blender, or at least my wacom tablet doesn't send it as such, and I've never been able to set it by actually pressing an eraser. I always have to select it in keymaps' mouse dropdown menu. I'm on windows, so I don't know if it would be any different on other OSes.
  Good luck if your pen driver/software doesn't have per-app keybindings. I'm sorry.

- If you clear the entry on any field with the X button it may linger and continue switching/acting on trigger as if it was still there. Just manually specify an empty entry (the text box won't be grayed out if you did this right) and that should fix it. You can X it again after if you really want to, it stays fixed after one attempt.

   ![image](https://github.com/user-attachments/assets/e67f4939-a3f8-4923-8c5c-bd3ee40c404b)

