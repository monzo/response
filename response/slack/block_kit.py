from django.conf import settings


class Message:
    def __init__(self):
        self.fallback_text = None
        self.blocks = []

    def set_fallback_text(self, text):
        self.fallback_text = text

    def add_block(self, block):
        self.blocks.append(block)

    def serialize(self):
        serialized = []
        for block in self.blocks:
            serialized.append(block.serialize())
        return serialized

    def send(self, channel, ts=None):
        """
        Build and send the message to the required channel
        """
        return settings.SLACK_CLIENT.send_or_update_message_block(
            channel, blocks=self.serialize(), fallback_text=self.fallback_text, ts=ts
        )


class Block:
    def __init__(self, block_id=None):
        self.block_id = block_id

    def serialize(self):
        raise NotImplementedError


class Section(Block):
    def __init__(self, block_id=None, text=None, accessory=None, fields=None):
        super().__init__(block_id=block_id)
        self.text = text
        self.accessory = accessory
        self.fields = fields

    def add_field(self, field):
        if not self.fields:
            self.fields = []
        self.fields.append(field)

    def serialize(self):
        block = {"type": "section"}

        if not (self.fields or self.text or self.accessory):
            raise ValueError

        if self.block_id:
            block["block_id"] = self.block_id

        if self.fields:
            block["fields"] = [t.serialize() for t in self.fields]
            return block

        if self.text:
            block["text"] = self.text.serialize()

        if self.accessory:
            block["accessory"] = self.accessory.serialize()

        return block


class Actions(Block):
    def __init__(self, block_id=None, elements=None):
        super().__init__(block_id=block_id)
        self.elements = elements

    def add_element(self, element):
        if not self.elements:
            self.elements = []

        self.elements.append(element)

    def serialize(self):
        block = {"type": "actions", "block_id": self.block_id}

        block["elements"] = [e.serialize() for e in self.elements]

        return block


class Divider(Block):
    def serialize(self):
        return {"type": "divider"}


class Confirm(Block):
    def __init__(self, title, text, confirm, deny):
        self.title = title
        self.text = text
        self.confirm = confirm
        self.deny = deny

    def serialize(self):
        return {
            "title": {"type": "plain_text", "text": self.title},
            "text": {"type": "mrkdwn", "text": self.text},
            "confirm": {"type": "plain_text", "text": self.confirm},
            "deny": {"type": "plain_text", "text": self.deny},
        }


class Button:
    def __init__(self, text, action_id, value=None, confirm=None):
        self.text = Text(text=text, text_type="plain_text")
        self.action_id = action_id
        self.value = value
        self.confirm = confirm

    def serialize(self):
        button = {
            "type": "button",
            "text": self.text.serialize(),
            "action_id": self.action_id,
        }

        if self.confirm:
            button["confirm"] = self.confirm.serialize()

        if self.value:
            button["value"] = str(self.value)

        return button


class Text:
    def __init__(self, text, title=None, text_type="mrkdwn", add_new_line=False):
        self.text_type = text_type
        self.text = text
        self.title = title
        self.add_new_line = add_new_line

    def serialize(self):
        text = f"{self.text}\n\u00A0" if self.add_new_line else self.text

        return {
            "type": self.text_type,
            "text": self.text if not self.title else f"*{self.title}*\n{text}",
        }


class StaticSelectOption:
    def __init__(self, text, value):
        self.text = text
        self.value = value

    def serialize(self):
        return {
            "text": {"type": "plain_text", "emoji": True, "text": self.text},
            "value": self.value,
        }


class StaticSelect:
    def __init__(self, options, action_id, placeholder_text=None):
        self.options = options
        self.placeholder_text = placeholder_text
        self.action_id = action_id

    def serialize(self):
        serialized = {
            "type": "static_select",
            "action_id": self.action_id,
            "options": [o.serialize() for o in self.options],
        }

        if self.placeholder_text:
            serialized["placeholder"] = {
                "type": "plain_text",
                "emoji": True,
                "text": self.placeholder_text,
            }

        return serialized
