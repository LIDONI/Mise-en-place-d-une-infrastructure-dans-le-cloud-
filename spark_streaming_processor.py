from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, IntegerType

# Création de la session Spark avec le connecteur Kafka
# Compatible avec PySpark installé via pip
spark = SparkSession.builder \
    .appName("RedpandaTicketStreaming") \
    .config("spark.jars.repositories", "https://repos.spark-packages.org/") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.1,org.apache.commons:commons-pool2:2.12.0") \
    .config("spark.sql.shuffle.partitions", "2") \
    .getOrCreate()

# Réduire le niveau de logs pour plus de lisibilité
spark.sparkContext.setLogLevel("WARN")

# Définition du schéma des tickets
schema = StructType() \
    .add("ticket_id", IntegerType()) \
    .add("client_id", IntegerType()) \
    .add("datetime", StringType()) \
    .add("demande", StringType()) \
    .add("type_demande", StringType()) \
    .add("priorite", StringType())

# Lecture du flux Redpanda (compatible Kafka)
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:19092") \
    .option("subscribe", "client_tickets") \
    .option("startingOffsets", "latest") \
    .load()

# Transformation JSON : extraire les champs depuis la colonne "value"
tickets = df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

console_query = tickets.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .start()

# Sauvegarde fichier JSON 
file_query = tickets.writeStream \
    .outputMode("append") \
    .format("json") \
    .option("path", "/data/output") \
    .option("checkpointLocation", "/data/checkpoints") \
    .start()

# 3. Attente
console_query.awaitTermination()