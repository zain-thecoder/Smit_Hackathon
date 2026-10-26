# SMART BUS TICKET BOOKING & RESERVATION SYSTEM
# Run: python main.py   (Python 3.8+, no external libraries, data in memory only)

APP_NAME = "SMART BUS RESERVATION SYSTEM"
LINE = "=" * 40
MAX_ATTEMPTS, MAX_AGE, EXIT_OPTION = 3, 120, 8
SUPPORTED_CITIES = ("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")
MENU = (
    "View Available Routes",
    "Search for a Route",
    "Book a Ticket",
    "View My Bookings",
    "Cancel a Booking",
    "View Seat Availability",
    "Generate Booking Report",
    "Exit",
)

# ---------- Task 02: data ----------
routes = [
    {
        "route_id": route_id,
        "departure_city": departure_city,
        "destination_city": destination_city,
        "departure_time": departure_time,
        "ticket_price": ticket_price,
        "total_seats": total_seats,
        "available_seats": total_seats,
    }
    for route_id, departure_city, destination_city, departure_time, ticket_price, total_seats in (
        ("R101", "Karachi", "Hyderabad", "08:00 AM", 1200, 40),
        ("R102", "Karachi", "Sukkur", "09:30 AM", 2000, 36),
        ("R103", "Hyderabad", "Mirpur Khas", "11:00 AM", 800, 32),
        ("R104", "Karachi", "Lahore", "07:00 PM", 5000, 45),
        ("R105", "Sukkur", "Hyderabad", "02:00 PM", 1500, 30),
    )
]
routes_by_id = {route["route_id"]: route for route in routes}
bookings, issued_booking_ids = [], set()


# ---------- helpers ----------
def journey(route):
    return f"{route['departure_city']} -> {route['destination_city']}"


def rupees(amount):
    return f"Rs. {amount:,}"


def seat_status(route):
    available = route["available_seats"]
    if available == 0:
        return "Fully Booked"
    if available == route["total_seats"]:
        return "Available"
    return "Partially Booked"


def header(title, width=40):
    print(f"\n{title}\n{'=' * width}")


def ask_yes_no(question):
    while True:
        answer = input(question).strip().lower()
        if answer in {"y", "yes", "n", "no"}:
            return answer[0] == "y"
        print("Please type y (yes) or n (no).")


def ask(prompt, check):
    """check(text) returns the value or raises ValueError. Up to 3 tries, else None."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return check(input(prompt).strip())
        except ValueError as error:
            print(f"  Error: {error} (Attempt {attempt}/{MAX_ATTEMPTS})")
    print("  Too many invalid attempts. Booking cancelled. No changes made.")
    return None


# ---------- Task 01: welcome + menu ----------
def show_menu():
    print(f"\n{APP_NAME}\n{LINE}")
    for number, item in enumerate(MENU, start=1):
        print(f"{number}. {item}")
    print(LINE)


def get_menu_choice():
    text = input("Enter your choice: ").strip()
    if text == "":
        print("Error: Choice cannot be empty. Please enter a number from 1 to 8.")
        return None
    if not text.isdigit():
        print(f"Error: '{text}' is not a number. Please enter 1 to 8.")
        return None
    choice = int(text)
    if not 1 <= choice <= EXIT_OPTION:
        print(f"Error: {choice} is not a valid option. Please choose 1 to {EXIT_OPTION}.")
        return None
    return choice


# ---------- Task 03 + 08: route tables ----------
def route_table(title, width, columns, row_formatter):
    header(title, width)
    only_available = ask_yes_no("Show only routes with seats available? (y/n): ")
    print(columns + "\n" + "-" * width)
    shown = 0
    for number, route in enumerate(routes, start=1):
        if only_available and route["available_seats"] == 0:
            continue
        print(row_formatter(number, route))
        shown += 1
    if shown == 0:
        print("No routes have seats available right now.")
    print("-" * width)
    return shown


def view_available_routes():
    shown = route_table(
        "AVAILABLE BUS ROUTES",
        84,
        f"{'No.':<5}{'Route':<8}{'Journey':<28}{'Depart':<11}{'Fare':<10}{'Seats':<8}Status",
        lambda number, route: (
            f"{number:<5}{route['route_id']:<8}{journey(route):<28}{route['departure_time']:<11}"
            f"{'Rs.' + str(route['ticket_price']):<10}"
            f"{str(route['available_seats']) + '/' + str(route['total_seats']):<8}{seat_status(route)}"
        ),
    )
    print(f"Routes shown: {shown} of {len(routes)}")


def view_seat_availability():
    route_table(
        "SEAT AVAILABILITY",
        78,
        f"{'Route':<8}{'Journey':<28}{'Available':<11}{'Booked':<8}{'Total':<7}Status",
        lambda number, route: (
            f"{route['route_id']:<8}{journey(route):<28}{route['available_seats']:<11}"
            f"{route['total_seats'] - route['available_seats']:<8}{route['total_seats']:<7}{seat_status(route)}"
        ),
    )


# ---------- Task 04: search ----------
def route_line(route):
    if route is None:
        return "No route found."
    seats = "Fully Booked" if route["available_seats"] == 0 else f"{route['available_seats']} seats available"
    return f"{route['route_id']} | {journey(route)} | Rs. {route['ticket_price']} | {seats}"


def search_route():
    header("SEARCH FOR A ROUTE")
    term = input("Search by route ID or city: ").strip()
    normalized_term = term.upper()
    if term == "":
        print("Error: Search term cannot be empty.")
        return
    if len(normalized_term) > 1 and normalized_term[0] == "R" and normalized_term[1:].isdigit():
        route = routes_by_id.get(normalized_term)
        print(route_line(route) if route else f"No route found with ID '{normalized_term}'.")
        return

    city = " ".join(term.lower().split())
    matches = [
        route for route in routes
        if city in (route["departure_city"].lower(), route["destination_city"].lower())
    ]
    for route in matches:
        print(route_line(route))
    if matches:
        print(f"{len(matches)} route(s) found.")
    else:
        print(f"No routes found for '{term}'. Try another city or route ID.")


# ---------- Task 05: book ticket ----------
def check_name(text):
    if not text:
        raise ValueError("Name cannot be empty.")
    return " ".join(text.split())


def check_age(text):
    if not text.isdigit():
        raise ValueError("Age must be a whole positive number.")
    age = int(text)
    if not 1 <= age <= MAX_AGE:
        raise ValueError(f"Age must be between 1 and {MAX_AGE}.")
    return age


def check_route(text):
    route_id = text.upper()
    if route_id not in routes_by_id:
        raise ValueError(f"Route '{route_id}' does not exist.")
    return routes_by_id[route_id]


def book_ticket():
    header("BOOK A TICKET")
    name = ask("Passenger name: ", check_name)
    age = name and ask("Passenger age: ", check_age)
    route = age and ask("Route ID (e.g. R101): ", check_route)
    if not route:
        return
    if route["available_seats"] == 0:
        print(f"  Sorry, route {route['route_id']} is Fully Booked. No changes made.")
        return

    def check_seats(text):
        if not text.isdigit():
            raise ValueError("Seats must be a whole positive number.")
        seat_count = int(text)
        if seat_count <= 0:
            raise ValueError("Seats must be greater than zero.")
        if seat_count > route["available_seats"]:
            raise ValueError(f"Only {route['available_seats']} seat(s) available on {route['route_id']}.")
        return seat_count

    seats = ask("Number of seats: ", check_seats)
    if seats is None:
        return

    booking_number = 1001 + len(issued_booking_ids)
    while f"B{booking_number}" in issued_booking_ids:
        booking_number += 1
    booking_id = f"B{booking_number}"
    fare = route["ticket_price"] * seats
    bookings.append(
        {
            "booking_id": booking_id,
            "passenger_name": name,
            "passenger_age": age,
            "route_id": route["route_id"],
            "seats": seats,
            "total_fare": fare,
            "status": "Confirmed",
        }
    )
    issued_booking_ids.add(booking_id)
    route["available_seats"] -= seats
    print(
        f"\nBooking confirmed!\nBooking ID: {booking_id}\nPassenger: {name} (Age {age})\n"
        f"Route: {route['route_id']} ({journey(route)}) at {route['departure_time']}\n"
        f"Seats booked: {seats}\nFare per seat: {rupees(route['ticket_price'])}\n"
        f"Total fare: {rupees(fare)}\nStatus: Confirmed\n"
        f"Seats left on {route['route_id']}: {route['available_seats']}/{route['total_seats']}"
    )


# ---------- Task 06: view bookings ----------
def view_bookings():
    header("MY BOOKINGS", 95)
    if not bookings:
        print("No bookings found.")
        return
    print(f"{'No.':<5}{'Booking':<9}{'Passenger':<18}{'Route':<7}{'Journey':<28}{'Seats':<7}{'Fare':<12}Status")
    print("-" * 95)
    for number, booking in enumerate(bookings, start=1):
        route = routes_by_id[booking["route_id"]]
        print(
            f"{number:<5}{booking['booking_id']:<9}{booking['passenger_name'][:17]:<18}{booking['route_id']:<7}"
            f"{journey(route):<28}{booking['seats']:<7}{rupees(booking['total_fare']):<12}{booking['status']}"
        )
    print("-" * 95 + f"\nTotal records: {len(bookings)}")


# ---------- Task 07: cancel booking ----------
def cancel_booking():
    header("CANCEL A BOOKING")
    if not bookings:
        print("No bookings found. Nothing to cancel.")
        return
    booking_id = input("Enter booking ID to cancel: ").strip().upper()
    if booking_id == "":
        print("Error: Booking ID cannot be empty. No changes made.")
        return
    for booking in bookings:
        if booking["booking_id"] == booking_id:
            break
    else:
        print(f"Booking {booking_id} not found. No changes made.")
        return
    route = routes_by_id[booking["route_id"]]
    if booking["status"] != "Confirmed":
        print(f"Booking {booking_id} is already {booking['status']}. Seats were NOT restored again.")
    elif route["available_seats"] + booking["seats"] > route["total_seats"]:
        print("Error: Seat data is inconsistent. Cancellation stopped. No changes made.")
    else:
        route["available_seats"] += booking["seats"]
        booking["status"] = "Cancelled"
        print(
            f"Booking {booking_id} has been cancelled.\nSeats restored: {booking['seats']}\n"
            f"Route {route['route_id']} available seats: {route['available_seats']}"
        )


# ---------- Task 09: report ----------
def generate_booking_report():
    seats_by_route = {}
    revenue_by_route = {}
    for booking in bookings:
        if booking["status"] != "Confirmed":
            continue
        route_id = booking["route_id"]
        seats_by_route[route_id] = seats_by_route.get(route_id, 0) + booking["seats"]
        revenue_by_route[route_id] = revenue_by_route.get(route_id, 0) + booking["total_fare"]

    header("BOOKING REPORT", 62)
    print(f"Route-wise confirmed bookings:\n  {'Route':<8}{'Journey':<28}{'Seats':<8}Revenue")
    for route in routes:
        route_id = route["route_id"]
        print(f"  {route_id:<8}{journey(route):<28}{seats_by_route.get(route_id, 0):<8}{rupees(revenue_by_route.get(route_id, 0))}")
    confirmed = sum(booking["status"] == "Confirmed" for booking in bookings)
    print("-" * 62)
    print(
        f"Total bookings created: {len(bookings)}\nConfirmed bookings: {confirmed}\n"
        f"Cancelled bookings: {sum(booking['status'] == 'Cancelled' for booking in bookings)}\n"
        f"Seats currently reserved: {sum(seats_by_route.values())}\n"
        f"Confirmed revenue: {rupees(sum(revenue_by_route.values()))}\n"
        f"Fully booked routes: {sum(route['available_seats'] == 0 for route in routes)}"
    )
    if seats_by_route:
        top_route = max(routes, key=lambda route: seats_by_route.get(route["route_id"], 0))
        print(f"Most popular route (by confirmed seats): {top_route['route_id']} ({seats_by_route[top_route['route_id']]} seats)")
    else:
        print("Most popular route: None yet (no confirmed bookings)")
    print("=" * 62)


# ---------- Task 10: schedule ----------
def show_route_schedule():
    header("ROUTE SCHEDULE BY DEPARTURE CITY")
    for city in SUPPORTED_CITIES:
        print(city)
        found_route = False
        for route in routes:
            if route["departure_city"] == city:
                print(f"  {route['route_id']} -> {route['destination_city']} | {route['departure_time']}")
                found_route = True
        if not found_route:
            print("  No scheduled departures.")


# ---------- main loop ----------
def report_and_schedule():
    generate_booking_report()
    if ask_yes_no("View route schedule by departure city? (y/n): "):
        show_route_schedule()


ACTIONS = {
    1: view_available_routes,
    2: search_route,
    3: book_ticket,
    4: view_bookings,
    5: cancel_booking,
    6: view_seat_availability,
    7: report_and_schedule,
}


def main():
    print(f"\n{LINE}\n{APP_NAME.center(40)}\n{'Book your bus ticket in a few steps'.center(40)}\n{LINE}")
    while True:
        show_menu()
        choice = get_menu_choice()
        if choice == EXIT_OPTION:
            print("Thank you for using Smart Bus Reservation System. Goodbye!")
            print("Note: All bookings were stored in memory only and are now cleared.")
            break
        if choice:
            ACTIONS[choice]()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram closed. Goodbye!")
