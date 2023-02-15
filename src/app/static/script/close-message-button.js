import { on_event, remove_parent_node } from "./helpers.js";

export function set_close_handler() {
  let message_paragraphs;
  message_paragraphs = document.getElementsByClassName('message-paragraph');
  for (let message_paragraph of message_paragraphs)
    message_paragraph.onclick = on_event(remove_parent_node, message_paragraph);
}
