import re
import json
import copy

# Define starting lineups for each team
team1_lineup = ["Luka Doncic", "Kyrie Irving", "Daniel Gafford", "P.J. Washington", "Derrick Jones Jr."]
team2_lineup = ["Jayson Tatum", "Jaylen Brown", "Jrue Holiday", "Derrick White", "Al Horford"]


def parse_play_by_play(play_by_play_text):
    """
    Parse the play-by-play text to identify matchups and events for an NBA game.

    Matchups are defined as periods where the same set of 5 players from each team
    are on the court without substitutions.

    Args:
        play_by_play_text (str): The raw play-by-play data as a string.

    Returns:
        list: A list of dictionaries, each representing a matchup with player lineups,
              events, and duration.
    """
    matchups = []

    # Initialize the current matchup
    current_matchup = {
        "players": {"team1": list(team1_lineup), "team2": list(team2_lineup)},
        "events": [],
        "matchup_duration": 0
    }

    last_time = "12:00"  # Track the last timestamp for duration calculations
    lines = play_by_play_text.strip().split("\n")  # Split play-by-play text into individual lines

    def convert_to_mm_ss_format(time_str):
        """
        Convert a time string in "ss.s" format to "mm:ss" format.
        """
        if re.match(r"^\d{1,2}\.\d$", time_str):
            seconds = float(time_str)
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes:02}:{seconds:02}"
        return time_str

    def finalize_matchup():
        """
        Finalize the current matchup and append it to the matchups list.
        """
        if current_matchup["events"]:
            matchups.append(copy.deepcopy(current_matchup))

    def add_time_to_duration(current_time):
        """
        Calculate the time duration between events and update the matchup duration.

        Args:
            current_time (str): The current timestamp in "mm:ss" format.
        """
        nonlocal last_time

        # Convert "ss.s" to "mm:ss" if necessary
        current_time = convert_to_mm_ss_format(current_time)

        start_minutes, start_seconds = map(int, last_time.split(":"))
        end_minutes, end_seconds = map(int, current_time.split(":"))

        duration = (start_minutes * 60 + start_seconds) - (end_minutes * 60 + end_seconds)

        # Adjust for end-of-quarter edge case
        if duration < 0:
            duration += 720

        current_matchup["matchup_duration"] += duration
        last_time = current_time

    for i, line in enumerate(lines):
        # Check for timestamp and update matchup duration
        time_match = re.search(r"(\d{1,2}:\d{2}|\d{1,2}\.\d)", line)
        if time_match:
            current_time = time_match.group(1)
            add_time_to_duration(current_time)

        # Handle substitutions
        if "enters the game for" in line:
            # Finalize the current matchup before a substitution
            finalize_matchup()

            # Start a new matchup with updated player lineups
            current_matchup = {
                "players": {"team1": list(current_matchup["players"]["team1"]),
                            "team2": list(current_matchup["players"]["team2"])},
                "events": [line],
                "matchup_duration": 0
            }

            # Process the substitution event
            parts = line.split(" enters the game for ")
            entering_player = parts[0].split(" - ")[1]
            exiting_player = parts[1]
            for team in ["team1", "team2"]:
                if exiting_player in current_matchup["players"][team]:
                    current_matchup["players"][team].remove(exiting_player)
                    current_matchup["players"][team].append(entering_player)
                    break

        # Add the current event to the matchup's events list
        current_matchup["events"].append(line)

    # Finalize the last matchup
    finalize_matchup()

    return matchups


def save_to_file(data, filename):
    """
    Save parsed matchups to a JSON file.

    Args:
        data (list): Parsed matchups data.
        filename (str): Path to the output JSON file.
    """
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Parsed matchups successfully saved to {filename}")
    except Exception as e:
        print(f"An error occurred while saving data: {e}")


def main():
    """
    Main function to parse play-by-play data and save matchups.
    """
    input_file = 'play_by_play1.txt'
    output_file = 'parsed_matchups1.json'

    try:
        with open(input_file, 'r') as file:
            play_by_play_text = file.read()
        print(f"Processing play-by-play data from {input_file}...")

        # Parse the play-by-play data
        parsed_matchups = parse_play_by_play(play_by_play_text)

        # Save the parsed matchups to a JSON file
        save_to_file(parsed_matchups, output_file)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
