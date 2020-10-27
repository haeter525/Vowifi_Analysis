from lib.Event import Event
from lib.Direction import Direction

class StateTree(object):
    """
    docstring
    """

    def __init(self):
        pass

    def next_state(self, direct, length, old_state):
        if direct != Direction.UPWARD.value and direct != Direction.DOWNWARD:
            raise f"Illage direction {direct}, use Enum lib.Direction."
        
        return predict([direct.value, length, old_state])

    def predict(self, data):
        dir, len, old_state = data[0]

        if len < 0: return old_state

        # One packet, one transition
        next_state = None

        if old_state == Event.NONE.value:
            # Area1

            if dir == Direction.UPWARD.value:
                if 800 < len < 1300:
                    return Event.INVITE1.value

            else : # DOWNWARD
                pass
            
        elif old_state == Event.INVITE1.value:

            if dir == Direction.UPWARD.value:
                pass

            else : # DOWNWARD
                if 250 < len < 600:
                    return Event.TRYING2.value
                elif 1100 < len < 1500:
                    return Event.SESSION3.value

        elif old_state == Event.TRYING2.value:

            if dir == Direction.UPWARD.value:
                if 800 < len < 1300:
                    return Event.PRACK4.value

            else : # DOWNWARD
                if 800 < len < 1300:
                    return Event.SESSION3.value

        elif old_state == Event.SESSION3.value:

            if dir == Direction.UPWARD.value:
                if 800 < len < 1300:
                    return Event.PRACK4.value

            else : # DOWNWARD
                if 500 < len < 1300:
                    return Event.OK5.value

        elif old_state == Event.PRACK4.value:

            if dir == Direction.UPWARD.value:
                if 250 < len < 1300:
                    return Event.OK5.value

            else : # DOWNWARD
                if 250 < len < 1300:
                    return Event.OK5.value

        elif old_state == Event.OK5.value:

            if dir == Direction.UPWARD.value:
                pass

            else : # DOWNWARD
                if len < 250:
                    return Event.RINGING6.value

        elif old_state == Event.RINGING6.value:
            # Area2

            if dir == Direction.UPWARD.value:
                if 800 < len < 1300:
                    return Event.PRACK7.value

            else : # DOWNWARD
                if 400 < len < 1000:
                    return Event.PRACK7.value

        elif old_state == Event.PRACK7.value:

            if dir == Direction.UPWARD.value:
                pass

            else : # DOWNWARD
                if len > 250:
                    return Event.OK8.value

        elif old_state == Event.OK8.value:
        
            if dir == Direction.UPWARD.value:
                if 400 < len < 1000:
                    return Event.ACK10.value

            else : # DOWNWARD
                if 400 < len < 1000:
                    return Event.OK9.value

        elif old_state == Event.OK9.value:
        
            if dir == Direction.UPWARD.value:
                if 400 < len < 1000:
                    return Event.ACK10.value

            else : # DOWNWARD
                pass

        elif old_state == Event.ACK10.value:
        
            if dir == Direction.UPWARD.value:
                if len < 250:
                    return Event.VOICE11.value

            else : # DOWNWARD
                if len < 250:
                    return Event.VOICE11.value

        elif old_state == Event.VOICE11.value:
        # Area3
        
            if len > 250:
                return Event.BYE12.value

        elif old_state == Event.BYE12.value:

            if len > 250:
                return Event.OK13.value

        elif old_state == Event.OK13.value:
            
            if len < 250:
                return Event.NONE.value

        return old_state
    