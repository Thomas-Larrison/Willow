import time
from datetime import datetime, timedelta
from rich.live import Live
from rich.table import Table
from rich.console import Console
from kraken_client import KrakenClient

console = Console()

client = KrakenClient()

def fetch_open_orders():
    urlpath = '/0/private/OpenOrders'
    nonce = int(time.time() * 1000)
    data = {'nonce': nonce}

    headers = {
        'API-Key': client.api_key,
        'API-Sign': client._sign(urlpath, data)
    }

    response = client.session.post(client.REST_API_URL + urlpath, headers=headers, data=data)
    return response.json().get('result', {}).get('open', {})


def fetch_closed_orders():
    urlpath = '/0/private/ClosedOrders'
    nonce = int(time.time() * 1000)
    data = {'nonce': nonce}

    headers = {
        'API-Key': client.api_key,
        'API-Sign': client._sign(urlpath, data)
    }

    response = client.session.post(client.REST_API_URL + urlpath, headers=headers, data=data)
    return response.json().get('result', {}).get('closed', {})


def generate_table():
    open_orders = fetch_open_orders()
    closed_orders = fetch_closed_orders()

    table = Table(title="Willow Bot Trade Watcher (Last 20 mins)")

    table.add_column("Type", style="cyan")
    table.add_column("Pair", style="yellow")
    table.add_column("Volume", justify="right")
    table.add_column("Price", justify="right")
    table.add_column("Status", style="green")
    table.add_column("PnL", justify="right", style="magenta")

    now = datetime.now()
    twenty_mins_ago = now - timedelta(minutes=20)

    for order in open_orders.values():
        descr = order['descr']
        opentm = datetime.fromtimestamp(order['opentm'])
        if opentm >= twenty_mins_ago:
            table.add_row(
                descr['type'].capitalize(),
                descr['pair'],
                order['vol'],
                descr.get('price', 'Market'),
                "Open",
                "-"
            )

    for order in closed_orders.values():
        closetm = datetime.fromtimestamp(order['closetm'])
        if closetm >= twenty_mins_ago:
            descr = order['descr']
            status = "Executed ✅" if order['status'] == 'closed' else order['status']
            price = float(order.get('price', 0))
            cost = float(order.get('cost', 0))
            fee = float(order.get('fee', 0))
            vol_exec = float(order.get('vol_exec', 0))
            pnl = cost - (price * vol_exec) - fee
            pnl_str = f"{pnl:.2f}"

            table.add_row(
                descr['type'].capitalize(),
                descr['pair'],
                order['vol_exec'],
                descr.get('price', 'Market'),
                status,
                pnl_str
            )

    return table


def main():
    with Live(generate_table(), refresh_per_second=0.5, console=console) as live:
        while True:
            time.sleep(5)
            live.update(generate_table())


if __name__ == "__main__":
    main()
