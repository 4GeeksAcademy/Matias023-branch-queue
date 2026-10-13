#!/usr/bin/env python3

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone


SERVICE_TYPES = ("deposito", "retiro", "gestion_cuenta")


@dataclass(frozen=True)
class Ticket:
    number: int
    client_name: str
    service_type: str
    issued_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class BranchQueue:
    def __init__(self):
        self._queues = {service: deque() for service in SERVICE_TYPES}
        self._next_number = 1

    def _validate_service(self, service_type: str) -> None:
        if service_type not in SERVICE_TYPES:
            raise ValueError(
                f"Invalid service type: {service_type}. "
                f"Valid options ar5: {', '.join(SERVICE_TYPES)}."
            )

    def issue_ticket(self, client_name: str, service_type: str) -> Ticket:
        client_name = client_name.strip()
        if not client_name:
            raise ValueError("Client name cannot be empty.")

        self._validate_service(service_type)

        ticket = Ticket(
            number=self._next_number,
            client_name=client_name,
            service_type=service_type,
         )
        self._next_number += 1
        self._queues[service_type].append(ticket)
        return ticket

    def call_next(self, service_type: str) -> Ticket:
        self._validate_service(service_type)
        queue = self._queues[service_type]
        if not queue:
            raise IndexError(
                f"No clients waiting for service: {service_type}."
            )
        return queue.popleft()

    def peek_next(self, service_type: str) -> Ticket:
        self._validate_service(service_type)
        queue = self._queues[service_type]
        if not queue:
            raise IndexError(
                f"No clients waiting for service: {service_type}."
            )
        return queue[0]

    def list_waiting(self) -> dict[str, list[Ticket]]:
        return {
            service: list(queue)
            for service, queue in self._queues.items()
        }

    def stats(self) -> dict[str, int]:
        result = {service: len(queue) for service, queue in self._queues.items()}
        result["total"] = sum(result.values())
        return result


def print_ticket(ticket: Ticket) -> None:
    print(
        f"# {ticket.number } | {ticket.client_name} | "
        f"{ticket.service_type} | {ticket.issued_at.isoformat()}"
    )


def run_cli() -> None:
    queue = BranchQueue()

    while True:
        print(
            "\n=== BRANCHUEUE ===\n"
            "1. Issue ticket\n"
            "2. Call next client\n"
            "3. Peek next client\n"
            "4. List waiting clients\n"
            "5. Show statistics\n"
            "6. Exit"
        )

        option = input("Choose an option: ").strip()

        if option == "1":
            name = input("Client name: ").strip()
            service = input(
                "Service (deposito/retiro/gestion_cuenta): "
            ).strip()

            try:
                ticket = queue.issue_ticket(name, service)
                print("Ticket issued successfully.")
                print_ticket(ticket)
            except ValueError as error:
                print(f"Error: {error}")

        elif option == "2":
            service = input("Service type: ").strip()
            try:
                ticket = queue.call_next(service)
                print("Calling next client:")
                print_ticket(ticket)
            except (ValueError, IndexError) as error:
                print(f"Error: {error}")

        elif option == "3":
            service = input("Service type: ").strip()
            try:
                print("Next client:")
                print_ticket(queue.peek_next(service))
            except (ValueError, IndexError) as error:
                print(f"Error: {error}")

        elif option == "4":
            waiting = queue.list_waiting()
            for service, tickets in waiting.items():
                print(f"\n{service}:")
                if not tickets:
                    print("  No clients waiting.")
                else:
                    for ticket in tickets:
                        print("  ", end="")
                        print_ticket(ticket)

        elif option == "5":
            print(queue.stats())

        elif option == "6":
            print("Goodbye.")
            break

        else:
            print("Invalid option. Choose a number from 1 to 6.")


if __name__ == "__main__":
    run_cli()
