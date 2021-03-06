from . import card
from .base import logger


class TableauPile:
    def __init__(self):
        self._hidden_deck = card.CardDeck()
        self._shown_deck = card.CardDeck()

    def take(self, n: int = 1) -> card.Card or card.Iterable:
        x = self._shown_deck.take(n)
        if not self._shown_deck and self._hidden_deck:
            self._shown_deck.put(self._hidden_deck.take(1))
        return x

    def peek(self):
        return self._shown_deck.deck

    def put(self, puts_card: card.Card or card.Iterable):
        self._shown_deck.put(puts_card)

    @property
    def deck(self):
        return self._shown_deck

    def __getitem__(self, item):
        return self._shown_deck[item]

    def __repr__(self):
        return f"<{type(self).__qualname__}: hidden={repr(self._hidden_deck)}, shown={repr(self._shown_deck)}>"

    def __str__(self):
        return f"TableauPile: {len(self._hidden_deck)} hidden, {self._shown_deck}"

    def __len__(self):
        return len(self._hidden_deck) + len(self._shown_deck)


class SuitDeck(card.CardDeck):
    def __init__(self, suit: card.CardSuit, full=False):
        self._suit = suit
        super().__init__(full)

    def __put(self, puts_card: card.Card):
        if self._suit == puts_card.suit:
            if (self.deck and puts_card.face.value - self.deck[-1].face.value == 1) or \
                    (not self.deck and puts_card.face == card.CardFace.ACE):
                self._deck.append(puts_card)
            else:
                raise ValueError("Card face is not after deck's last card face")
        else:
            raise ValueError("Card does not match deck")

    def take(self, n=0):
        raise NotImplementedError

    def __repr__(self):
        return f"<{type(self).__qualname__}: " \
            f"[{', '.join([repr(card) for card in self._deck]).strip()}], suit={self._suit}>"


class MoveError(Exception):
    pass


class Game:
    def __init__(self):
        self.base_deck = card.CardDeck(full=True)

        # decks are generated left to right
        self.decks = [TableauPile() for __ in range(7)]
        for i, v in enumerate(self.decks):
            for __ in range(i + 1):
                v._hidden_deck.put(self.base_deck.take())

            # show one card
            v._shown_deck.put(v._hidden_deck.take())

        self.foundations = {k.value: SuitDeck(k) for k in card.CardSuit}

        self.hand_deck = card.CardDeck()

        self.debug()

    def debug(self):
        logger.debug(f"base deck: {self.base_deck}")

        x = '\n'.join(["deck " + str(i + 1) + ": " + str(v) for i, v in enumerate(self.decks)])
        logger.debug(f"TableauPile: \n{x}")

        logger.debug(f"foundations: {self.foundations}")
        logger.debug(f"hand: {self.hand_deck}")

    def move_info(self):
        print("""XX CN    CN CN CN CN

CN XX XX XX XX XX XX
   CN XX XX XX XX XX
      CN XX XX XX XX
         CN XX XX XX
            CN XX XX
               CN XX
                  CN""")

    def place(self, take_number: int, take_index: int, put_index: int):
        if take_index == 0:
            if take_number > 1:
                raise MoveError("can only take 1 card at a time from the main deck")

            if self.peek_verify(put_index, self.base_deck.deck[-1]):
                self.hand_deck.put(self.base_deck.take(take_number))
                self.decks[put_index].put(self.hand_deck.take(card.MAX_CARDS))
                return self
            else:
                raise MoveError("invalid move")

        if not put_index:
            raise MoveError("cannot place cards into main deck")

        if self.peek_verify(put_index, self.decks[take_index].peek()[-1]):
            self.hand_deck.put(self.decks[take_index].take(take_number))
            self.decks[put_index].put(self.hand_deck.take(card.MAX_CARDS))
            return self
        else:
            raise MoveError("invalid move")

    def peek_verify(self, deck_index: int, peeked_card: card.Card) -> bool:
        if len(self.decks[deck_index]):
            return self.decks[deck_index][-1].face.value - peeked_card.face.value == 1 \
                   and not peeked_card.suit.is_same_color(self.decks[deck_index][-1].suit)
        else:
            return card.CardFace.KING == peeked_card.face.value
