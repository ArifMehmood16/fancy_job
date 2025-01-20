from datetime import datetime, timedelta

def generate_commit_schedule(message, start_date="2025-01-01"):
    import numpy as np
    import pyfiglet

    def text_to_dynamic_grid(message, font="5x7"):
        ascii_art = pyfiglet.Figlet(font=font).renderText(message)
        lines = ascii_art.splitlines()
        grid = np.array([[1 if char != ' ' else 0 for char in line] for line in lines if line.strip()])
        # Ensure the grid is 7 rows tall (pad if necessary)
        if grid.shape[0] < 7:
            padding = 7 - grid.shape[0]
            grid = np.pad(grid, ((0, padding), (0, 0)), mode='constant')
        return grid

    def map_grid_to_dates(grid, start_date):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        dates = []
        for col in range(grid.shape[1]):  # For each column
            for row in range(grid.shape[0]):  # For each row in the column
                days_offset = col * 7 + row
                commit_date = start_date + timedelta(days=days_offset)
                if grid[row, col] == 1:  # If the grid cell requires a commit
                    dates.append(commit_date.strftime("%Y-%m-%d"))
        return dates

    # Convert the message to a dynamic grid and map the grid to dates
    grid = text_to_dynamic_grid(message)
    return map_grid_to_dates(grid, start_date)

def is_date_in_commit_schedule(message, date, start_date="2025-01-19"):
    commit_dates = generate_commit_schedule(message, start_date)
    return date in commit_dates

def main():
    try:
        today_date = datetime.today().strftime("%Y-%m-%d")
        output = is_date_in_commit_schedule("ARIF 25 !", today_date, "2025-01-19")
        print(today_date)
        print(output)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
