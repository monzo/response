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

    def open_modal(
        self, trigger_id, callback_id, title, submit, close, private_metadata=None
    ):
        return settings.SLACK_CLIENT.open_modal(
            trigger_id,
            callback_id,
            title,
            submit,
            close,
            self.serialize(),
            private_metadata=private_metadata,
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
    def __init__(self, title, text, confirm, deny, block_id=None):
        super().__init__(block_id=block_id)
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


class Text(Block):
    def __init__(
        self, text, title=None, text_type="mrkdwn", add_new_line=False, block_id=None
    ):
        super().__init__(block_id=block_id)
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


class Context(Block):
    def __init__(self, text):
        self.text = text

    def serialize(self):
        return {"type": "context", "elements": [{"type": "mrkdwn", "text": self.text}]}


#
#  These are action accessories for inside section blocks
#
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


#
# These are inputs
#


class PlainTextInput(Block):
    def __init__(
        self,
        label,
        action_id,
        initial_value=None,
        placeholder_text=None,
        multiline=False,
        optional=False,
        block_id=None,
    ):
        super().__init__(block_id=block_id)
        self.label = label
        self.initial_value = initial_value
        self.placeholder_text = placeholder_text
        self.action_id = action_id
        self.multiline = multiline
        self.optional = optional

    def serialize(self):
        block = {
            "block_id": self.block_id,
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "multiline": self.multiline,
                "action_id": self.action_id,
            },
            "label": {"type": "plain_text", "text": self.label, "emoji": True},
            "optional": self.optional,
        }

        if self.placeholder_text:
            block["element"]["placeholder"] = {
                "type": "plain_text",
                "text": self.placeholder_text,
            }

        if self.initial_value:
            block["element"]["initial_value"] = self.initial_value

        print(block)
        return block


class StaticSelectInput(Block):
    def __init__(
        self,
        label,
        options,
        action_id,
        initial_option=None,
        placeholder_text=None,
        optional=False,
        block_id=None,
    ):
        super().__init__(block_id=block_id)
        self.label = label
        self.options = options
        self.placeholder_text = placeholder_text
        self.action_id = action_id
        self.optional = optional
        self.initial_option = initial_option

    def serialize(self):
        serialized = {
            "block_id": self.block_id,
            "type": "input",
            "element": {
                "type": "static_select",
                "action_id": self.action_id,
                "options": [o.serialize() for o in self.options],
            },
            "optional": self.optional,
            "label": {"type": "plain_text", "text": self.label, "emoji": True},
        }

        if self.placeholder_text:
            serialized["element"]["placeholder"] = {
                "type": "plain_text",
                "emoji": True,
                "text": self.placeholder_text,
            }

        if self.initial_option:
            serialized["element"]["initial_option"] = self.initial_option

        return serialized


class UserSelect(Block):
    def __init__(
        self,
        label,
        action_id,
        block_id=None,
        initial_user=None,
        placeholder_text=None,
        optional=False,
    ):
        super().__init__(block_id=block_id)
        self.label = label
        self.initial_user = initial_user
        self.placeholder_text = placeholder_text
        self.action_id = action_id
        self.optional = optional

    def serialize(self):
        serialized = {
            "block_id": self.block_id,
            "type": "input",
            "element": {
                "type": "users_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": self.placeholder_text,
                    "emoji": True,
                },
                "action_id": self.action_id,
            },
            "optional": self.optional,
            "label": {"type": "plain_text", "text": self.label, "emoji": True},
        }

        if self.initial_user:
            serialized["element"]["initial_user"] = self.initial_user

        return serialized
