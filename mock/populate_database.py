import random
from datetime import datetime, timedelta

table_name = 'lamp01'

# Gerar timestamps e inserir dados na tabela
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)

while start_date <= end_date:
    num_timestamps = random.randint(0, 200)

    for _ in range(num_timestamps):
        # Adiciona horas, minutos e segundos aleatórios
        random_time = timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )

        current_timestamp = start_date + random_time

        seconds = random.randint(15000, 30000)

        # Printando o comando SQL em vez de executá-lo
        sql_command = f"INSERT INTO {table_name} (recvTime, attrValue) VALUES ('{current_timestamp}', {seconds});"
        print(sql_command)

        # Intervalo aleatório de 0 a 2 dias sem criar timestamps
        start_date += timedelta(days=random.randint(0, 2))
