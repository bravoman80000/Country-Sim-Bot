# year_tracker.py

# Initialize the in-game year and turn
current_year = 1
current_turn = 1

# Function to manually set the year
def set_year(year):
    global current_year
    current_year = year
    return f"Year manually set to {current_year}."

# Function to manually set the turn
def set_turn(turn):
    global current_turn
    current_turn = turn
    return f"Turn manually set to {current_turn}."

# Function to advance the year
def advance_year():
    global current_year
    current_year += 1
    return f"Year {current_year}: The next chapter begins..."

# Function to advance the turn
def advance_turn():
    global current_turn
    current_turn += 1
    return f"Turn {current_turn}: The next phase begins..."

# Function to handle events that trigger based on the current year
def trigger_event():
    if current_year == 5:
        return "Event: The first trade agreement is signed with neighboring countries."
    elif current_year == 10:
        return "Event: The technological breakthrough in energy production boosts your economy."
    elif current_year == 15:
        return "Event: Political unrest spreads due to increasing taxes."
    elif current_year == 20:
        return "Event: The outbreak of a global war changes the balance of power."
    return None

# Function to start a new turn, increment year and turn, and trigger events
def start_new_turn():
    year_message = advance_year()  # Advance to the next year
    turn_message = advance_turn()  # Advance to the next turn
    event = trigger_event()       # Check for any events
    message = f"{year_message}\n{turn_message}"
    if event:
        message += f"\n{event}"  # Append the event message if triggered
    return message
