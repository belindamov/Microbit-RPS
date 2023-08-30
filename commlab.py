import microbit  # Do not change these to star imports, the test code neds them
import utime  # like this to work properly!
import radio

# Global constants

ROCK = microbit.Image('00000:09990:09990:09990:00000')
PAPER = microbit.Image('99999:90009:90009:90009:99999')
SCISSORS = microbit.Image('99009:99090:00900:99090:99009')
RPS = (b'R', b'P', b'S')

MYID = b'41'  # TODO: change this to be the same as your assigned micro:bit number


def choose_opponent():
    # """ Return the opponent id from button presses
    #
    # Returns
    # -------
    # byte string:
    #     A two-character byte string representing the opponent ID
    #
    # Notes
    # -------
    # Button A is used to increment a digit of the ID
    # Button B is used to 'lock in' the digit and move on
    # """
    #
    # This function is complete.

    # Initialization
    num = [0] * 2
    idx = 0

    # Main loop over digits
    while idx < len(num):
        microbit.sleep(100)
        # Display only the last character of the hex representation (skip the 0x part)
        microbit.display.show(hex(num[idx])[-1], wait=False)
        # The button increments the digit mod 16, to make sure it's a single hex digit
        if microbit.button_a.was_pressed():
            num[idx] = (num[idx] + 1) % 16
        # Show a different character ('X') to indicate a selection
        if microbit.button_b.was_pressed():
            microbit.display.show('X')
            idx += 1
    microbit.display.clear()

    # Make sure we return a byte string, rather than a standard string.
    return bytes(''.join(hex(n)[-1] for n in num), 'UTF-8')


def choose_play():
    # """ Returns the play selected from button presses
    #
    # Returns
    # -------
    # byte string:
    #     A single-character byte string representing a move,
    # as given in the RPS list at the top of the file.
    #
    # Notes
    # -----
    # Button A is used to iterate between the options of rock, paper, and scissors
    # Button B is used to confirm your choice of play
    # """
    #
    # TODO: write code

    # List of visual representations on the microbit of rock, paper, and scissors
    pictures = [ROCK, PAPER, SCISSORS]

    # Initialise idx and count as 0
    idx = 0
    count = 0

    # While loop that runs until count is 1
    while count < 1:
        microbit.sleep(100)
        # Show the visual representation of rock, paper, or scissors on the microbit depending on idx value
        microbit.display.show(pictures[idx])
        # If button A is pressed, make idx increase by 1 (idx can not go above 2 and will instead loop back to 0 after)
        if microbit.button_a.was_pressed():
            idx = (idx + 1) % 3
        # If button B is pressed, display 'X' on the microbit to show that the decision is locked in and add 1 to count
        if microbit.button_b.was_pressed():
            microbit.display.show('X')
            count += 1
    # Clear the display on the microbit
    microbit.display.clear()

    # Return the move via the RPS tuple, using idx as the index value
    return RPS[idx]


def send_choice(opponent_id, play, round_number):
    # """ Sends a message via the radio
    #
    # Parameters
    # ----------
    # opponent_id  : byte string
    #     The id of the opponent
    # play         : byte string
    #     One of b'R', b'P', or b'S'
    # round_number : int
    #     The round that is being played
    #
    # Returns
    # -------
    # int:
    #     Time that the message was sent
    # """
    #
    # TODO: write code

    # Convert round_number from type int to string
    round_number = str(round_number)
    # Convert round_number from type string to bytes
    round_number = bytes(round_number, 'UTF-8')
    # Combine the byte strings into one byte string
    byte_string = opponent_id + MYID + play + round_number

    # Send the byte string via radio
    radio.send_bytes(byte_string)

    # Return the time
    return utime.ticks_ms()


def send_acknowledgement(opponent_id, round_number):
    # """ Sends an acknowledgement message
    #
    # Parameters
    # ----------
    # opponent_id  : bytes
    #     The id of the opponent
    # round_number : int
    #     The round that is being played
    # """
    #
    # TODO: write code

    # Initialise action_value
    action_value = b'X'

    # Convert round_number from type int to string
    round_number = str(round_number)
    # Convert round_number from type string to bytes
    round_number = bytes(round_number, 'UTF-8')

    # Combine the byte strings into one byte string
    byte_string = opponent_id + MYID + action_value + round_number

    # Send the byte string via radio
    radio.send_bytes(byte_string)


def parse_message(opponent_id, round_number):
    # """ Receive and parse the next valid message
    #
    # Parameters
    # ----------
    # opponent_id  : bytes
    #     The id of the opponent
    # round_number : int
    #     The round that is being played
    #
    # Returns
    # -------
    # bytes :
    #     The contents of the message, if it is valid
    # None :
    #     If the message is invalid or does not need further processing
    #
    # Notes
    # -----
    # This function sends an acknowledgement using send_acknowledgement() if
    # the message is valid and contains a play (R, P, or S), using the round
    # number from the message.
    # """
    #
    # TODO: write code

    # Receive the next message in the queue via the radio
    message = radio.receive_bytes()

    # Check if there is a message
    if message is not None:
        # Check if the message is of a valid length
        if 5 < len(message) < 10:
            # Splice the message to get the contents of it
            my_id = message[0:2]
            opponent = message[2:4]
            action = message[4:5]
            round_value = message[5:len(message)]

            # Check that the contents of the message match up with the expected message structure
            if my_id == MYID and opponent == opponent_id and int(round_value) == round_number:
                # Check if the actions are b'R', b'P', or b'S'
                if action == b'R' or action == b'P' or action == b'S':
                    # Send an acknowledgement
                    send_acknowledgement(opponent_id, round_number)
                    # Return the action
                    return action
                # If the action is b'X', return the action with no acknowledgement sent
                elif action == b'X':
                    return action

            # If statement for if the contents of the message match up but the round received is a past round
            if my_id == MYID and opponent == opponent_id and int(round_value) < round_number:
                # Check if the actions are b'R', b'P', or b'S'
                if action == b'R' or action == b'P' or action == b'S':
                    # Send an acknowledgement
                    send_acknowledgement(opponent_id, int(round_value))
                    # Return None
                    return None
                # If the action is b'X', return None and send no acknowledgement
                elif action == b'X':
                    return None

    # If message is invalid, return None
    return None


def resolve(my, opp):
    # """ Returns the outcome of a rock-paper-scissors match
    # Also displays the result
    #
    # Parameters
    # ----------
    # my  : bytes
    #     The choice of rock/paper/scissors that this micro:bit made
    # opp : bytes
    #     The choice of rock/paper/scissors that the opponent micro:bit made
    #
    # Returns
    # -------
    # int :
    #     Numerical value for the outcome as listed below
    #      0: Loss/Draw
    #     +1: Win
    #
    # Notes
    # -----
    # Input parameters should be one of b'R', b'P', b'S'
    #
    # Examples
    # --------
    # solve(b'R', b'P') returns 0 (Loss)
    # solve(b'R', b'S') returns 1 (Win)
    # solve(b'R', b'R') returns 0 (Draw)
    #
    # """
    #
    # This function is complete.

    # Use fancy list indexing tricks to resolve the match
    diff = RPS.index(my) - RPS.index(opp)
    result = [0, 1, 0][diff]

    # Display a cute picture to show what happened
    faces = [microbit.Image.ASLEEP, microbit.Image.HAPPY, microbit.Image.SAD]
    microbit.display.show(faces[diff])
    # Leave the picture up for long enough to see it
    microbit.sleep(333)
    return result


def display_score(score, times=3):
    # """ Flashes the score on the display
    #
    # Parameters
    # ----------
    # score : int
    #     The current score
    # times : int
    #     Number of times to flash
    #
    # Returns
    # -------
    # None
    #
    # Notes
    # -----
    # If the score is greater than 9 it scrolls, rather than flashing.
    # """
    #
    # This function is complete.

    screen_off = microbit.Image(':'.join(['0' * 5] * 5))
    if score < 9 and score >= 0:
        microbit.display.show([screen_off, str(score)] * times)
    elif score > 9:
        for n in range(times):
            microbit.display.scroll(str(score))
            microbit.display.show(screen_off)
            microbit.sleep(333)


def main():
    # """ Main control loop"""
    #
    # TODO: fill in parts of code below as marked.

    # set up the radio for a moderate range
    radio.config(power=6, queue=50)
    radio.on()

    # initialise score and round number
    score = 0
    round_number = 0

    # select an opponent
    opponent_id = choose_opponent()

    # Run an arbitrarily long RPS contest
    while True:
        # get a play from the buttons
        choice = choose_play()
        # send choice
        send_time = send_choice(opponent_id, choice, round_number)

        acknowledged, resolved = (False, False)
        # passive waiting display
        microbit.display.show(microbit.Image.ALL_CLOCKS, wait=False, loop=True)
        while not (acknowledged and resolved):
            # get a message from the radio
            message = parse_message(opponent_id, round_number)
            # TODO: if is a play
            if message == b'R' or message == b'P' or message == b'S':
                # resolve the match and display the result
                result = resolve(choice, message)
                microbit.display.show(result)
                microbit.sleep(333)
                # TODO: update score
                score = score + result
                resolved = True
                # display the score
                display_score(score)

            # TODO: if is acknowledgement
            if message == b'X':
                acknowledged = True

            # TODO: handle situation if not acknowledged
            if not acknowledged:
                time_now = utime.ticks_ms()
                if time_now - send_time > 3000:
                    send_time = send_choice(opponent_id, choice, round_number)

        # TODO: Update round number
        round_number += 1

# Do not modify the below code, this makes sure your program runs properly!

if __name__ == "__main__":
    main()
