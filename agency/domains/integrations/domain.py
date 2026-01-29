from typing import Dict, Any
from ...core.base_domain import BaseDomain, DomainInput, DomainOutput
import json


class IntegrationsDomain(BaseDomain):
    """Domain responsible for system integrations including APIs, data flows, and third-party services"""

    def __init__(self, name: str = "integrations", description: str = "Manages system integrations including APIs, data flows, and third-party services", resource_manager=None, cache_enabled: bool = True):
        super().__init__(name=name, description=description, resource_manager=resource_manager, cache_enabled=cache_enabled)
        self.integration_types = [
            "api_integration", "data_pipeline", "event_streaming", 
            "webhook_handler", "oauth_connector", "messaging_system"
        ]
        self.protocols = ["rest", "graphql", "grpc", "soap", "mqtt", "amqp", "websocket"]
        self.third_party_services = [
            "stripe", "paypal", "twilio", "sendgrid", "mailchimp", 
            "slack", "discord", "github", "salesforce", "hubspot"
        ]
        self.messaging_platforms = ["kafka", "rabbitmq", "redis", "sns_sqs", "pubsub"]
        self.integration_templates = {
            "api_integration": self._generate_api_integration_template,
            "data_pipeline": self._generate_data_pipeline_template,
            "event_streaming": self._generate_event_streaming_template,
            "webhook_handler": self._generate_webhook_handler_template,
            "oauth_connector": self._generate_oauth_connector_template,
            "messaging_system": self._generate_messaging_system_template
        }

    async def execute(self, input_data: DomainInput) -> DomainOutput:
        """Generate integration code based on the input specification"""
        try:
            # Acquire resources before executing
            if not await self.resource_manager.acquire_resources(self.name):
                return DomainOutput(
                    success=False,
                    error=f"Resource limits exceeded for domain {self.name}"
                )

            try:
                query = input_data.query.lower()
                context = input_data.context
                params = input_data.parameters

                # Determine the type of integration to generate
                integration_type = self._determine_integration_type(query)
                protocol = params.get("protocol", context.get("protocol", "rest"))
                third_party_service = params.get("third_party_service", context.get("third_party_service", "generic"))
                messaging_platform = params.get("messaging_platform", context.get("messaging_platform", "kafka"))

                if integration_type not in self.integration_types:
                    return DomainOutput(
                        success=False,
                        error=f"Integration type '{integration_type}' not supported. Available types: {', '.join(self.integration_types)}"
                    )

                # Generate the integration code
                generated_code = self._generate_integration_code(integration_type, query, protocol, third_party_service, messaging_platform, params)

                # Enhance the code if other domains are available
                enhanced_code = await self._enhance_with_other_domains(generated_code, input_data)

                return DomainOutput(
                    success=True,
                    data={
                        "code": enhanced_code,
                        "integration_type": integration_type,
                        "protocol": protocol,
                        "third_party_service": third_party_service,
                        "messaging_platform": messaging_platform,
                        "original_query": query
                    },
                    metadata={
                        "domain": self.name,
                        "enhanced": enhanced_code != generated_code
                    }
                )
            finally:
                # Always release resources after execution
                self.resource_manager.release_resources(self.name)
        except Exception as e:
            return DomainOutput(
                success=False,
                error=f"Integration code generation failed: {str(e)}"
            )

    def can_handle(self, input_data: DomainInput) -> bool:
        """Determine if this domain can handle the input"""
        query = input_data.query.lower()

        # Check for keywords that suggest integration development
        integration_keywords = [
            "integration", "api integration", "data pipeline", "event streaming", 
            "webhook", "oauth", "connector", "messaging", "queue", 
            "stripe", "paypal", "twilio", "sendgrid", "mailchimp", 
            "slack", "discord", "github", "salesforce", "hubspot", 
            "rest api", "graphql", "grpc", "soap", "mqtt", "amqp", 
            "kafka", "rabbitmq", "redis", "sns", "sqs", "pubsub", 
            "connect to", "integrate with", "sync data", "data flow", 
            "third party", "external service", "payment gateway", 
            "notification service", "crm integration", "erp integration"
        ]

        return any(keyword in query for keyword in integration_keywords)

    def _determine_integration_type(self, query: str) -> str:
        """Determine what type of integration to generate based on the query"""
        if any(word in query for word in ["api integration", "rest api", "graphql", "grpc", "soap"]):
            return "api_integration"
        elif any(word in query for word in ["data pipeline", "etl", "data sync", "extract transform load"]):
            return "data_pipeline"
        elif any(word in query for word in ["event streaming", "streaming", "real time", "kafka", "pubsub"]):
            return "event_streaming"
        elif any(word in query for word in ["webhook", "callback", "incoming hook"]):
            return "webhook_handler"
        elif any(word in query for word in ["oauth", "authentication", "login", "social login"]):
            return "oauth_connector"
        elif any(word in query for word in ["messaging", "queue", "kafka", "rabbitmq", "redis"]):
            return "messaging_system"
        else:
            return "api_integration"  # Default to API integration

    def _generate_integration_code(self, integration_type: str, query: str, protocol: str, third_party_service: str, messaging_platform: str, params: Dict[str, Any]) -> str:
        """Generate integration code based on type, query, and protocol"""
        if integration_type in self.integration_templates:
            return self.integration_templates[integration_type](query, protocol, third_party_service, messaging_platform, params)
        else:
            return self._generate_generic_integration_code(query, integration_type, protocol, third_party_service, messaging_platform, params)

    def _generate_api_integration_template(self, query: str, protocol: str, third_party_service: str, messaging_platform: str, params: Dict[str, Any]) -> str:
        """Generate an API integration template based on the query"""
        if protocol == "rest" and third_party_service == "stripe":
            return f"""import stripe
import os
from typing import Dict, Any

class StripeIntegration:
    """
    Stripe API Integration for {query}
    Handles payments, subscriptions, and customer management
    """
    
    def __init__(self):
        # Initialize Stripe with secret key from environment
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    def create_customer(self, email: str, name: str) -> Dict[str, Any]:
        """
        Create a new customer in Stripe
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                description=f"Customer for {query}"
            )
            return {{
                'success': True,
                'customer_id': customer.id,
                'customer': customer
            }}
        except stripe.error.StripeError as e:
            return {{
                'success': False,
                'error': str(e)
            }}

    def create_payment_intent(self, amount: int, currency: str = 'usd', customer_id: str = None) -> Dict[str, Any]:
        """
        Create a payment intent for processing payments
        Amount should be in cents (e.g., $10.00 = 1000)
        """
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                automatic_payment_methods={{
                    'enabled': True,
                }},
            )
            return {{
                'success': True,
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id
            }}
        except stripe.error.StripeError as e:
            return {{
                'success': False,
                'error': str(e)
            }}

    def create_subscription(self, customer_id: str, price_id: str) -> Dict[str, Any]:
        """
        Create a subscription for a customer
        """
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{{'price': price_id}}],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent']
            )
            return {{
                'success': True,
                'subscription_id': subscription.id,
                'subscription': subscription
            }}
        except stripe.error.StripeError as e:
            return {{
                'success': False,
                'error': str(e)
            }}

    def handle_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Handle incoming webhook events from Stripe
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            
            # Process different event types
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                # Fulfill the purchase
                print(f"Payment succeeded for amount: {{payment_intent['amount']}}")
                
            elif event['type'] == 'customer.subscription.created':
                subscription = event['data']['object']
                # Grant access to the subscribed service
                print(f"New subscription created: {{subscription['id']}}")
                
            return {{
                'success': True,
                'event_type': event['type'],
                'processed': True
            }}
        except ValueError:
            # Invalid payload
            return {{
                'success': False,
                'error': 'Invalid payload'
            }}
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return {{
                'success': False,
                'error': 'Invalid signature'
            }}
"""
        elif protocol == "rest" and third_party_service == "twilio":
            return f"""from twilio.rest import Client
import os
from typing import Dict, Any

class TwilioIntegration:
    """
    Twilio API Integration for {query}
    Handles SMS, voice calls, and messaging
    """
    
    def __init__(self):
        # Initialize Twilio with credentials from environment
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.client = Client(account_sid, auth_token)
        self.from_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

    def send_sms(self, to: str, message: str) -> Dict[str, Any]:
        """
        Send an SMS message
        """
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_phone_number,
                to=to
            )
            return {{
                'success': True,
                'message_sid': message.sid,
                'status': message.status
            }}
        except Exception as e:
            return {{
                'success': False,
                'error': str(e)
            }}

    def send_bulk_sms(self, recipients: list, message: str) -> Dict[str, Any]:
        """
        Send SMS messages to multiple recipients
        """
        results = []
        for recipient in recipients:
            result = self.send_sms(recipient, message)
            results.append(result)
        
        successful_sends = sum(1 for r in results if r['success'])
        return {{
            'total_sent': len(results),
            'successful_sends': successful_sends,
            'failed_sends': len(results) - successful_sends,
            'details': results
        }}

    def make_call(self, to: str, twiml_url: str) -> Dict[str, Any]:
        """
        Make a phone call using TwiML URL
        """
        try:
            call = self.client.calls.create(
                url=twiml_url,
                to=to,
                from_=self.from_phone_number
            )
            return {{
                'success': True,
                'call_sid': call.sid,
                'status': call.status
            }}
        except Exception as e:
            return {{
                'success': False,
                'error': str(e)
            }}

    def get_call_logs(self, limit: int = 20) -> Dict[str, Any]:
        """
        Retrieve call logs
        """
        try:
            calls = self.client.calls.list(limit=limit)
            call_logs = []
            for call in calls:
                call_logs.append({{
                    'sid': call.sid,
                    'from': call.from_,
                    'to': call.to,
                    'duration': call.duration,
                    'status': call.status,
                    'date_created': call.date_created.isoformat()
                }})
            return {{
                'success': True,
                'calls': call_logs
            }}
        except Exception as e:
            return {{
                'success': False,
                'error': str(e)
            }}
"""
        else:
            return f"""# API Integration for {query}
# Protocol: {protocol}
# Third Party Service: {third_party_service}

# Generic API integration template
import requests
import json
from typing import Dict, Any

class {third_party_service.capitalize()}Integration:
    """
    {third_party_service.capitalize()} API Integration for {query}
    """
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or self._get_api_key()
        self.base_url = base_url or self._get_base_url()
        self.headers = {{
            'Authorization': f'Bearer {{self.api_key}}',
            'Content-Type': 'application/json'
        }}

    def _get_api_key(self) -> str:
        # Retrieve API key from environment or configuration
        import os
        return os.getenv('{third_party_service.upper()}_API_KEY', '')

    def _get_base_url(self) -> str:
        # Return the base URL for the API
        return 'https://api.{third_party_service.lower()}.com/v1'

    def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to the {third_party_service} API
        """
        url = f'{{self.base_url}}{{endpoint}}'
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                return {{'success': False, 'error': 'Unsupported HTTP method'}}
            
            if response.status_code in [200, 201, 204]:
                return {{
                    'success': True,
                    'data': response.json() if response.content else None,
                    'status_code': response.status_code
                }}
            else:
                return {{
                    'success': False,
                    'error': response.text,
                    'status_code': response.status_code
                }}
        except requests.exceptions.RequestException as e:
            return {{
                'success': False,
                'error': str(e)
            }}

    def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """
        Get a specific resource by ID
        """
        return self.make_request('GET', f'/resources/{{resource_id}}')

    def create_resource(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new resource
        """
        return self.make_request('POST', '/resources', data)

    def update_resource(self, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing resource
        """
        return self.make_request('PUT', f'/resources/{{resource_id}}', data)

    def delete_resource(self, resource_id: str) -> Dict[str, Any]:
        """
        Delete a resource
        """
        return self.make_request('DELETE', f'/resources/{{resource_id}}')
"""
    
    def _generate_data_pipeline_template(self, query: str, protocol: str, third_party_service: str, messaging_platform: str, params: Dict[str, Any]) -> str:
        """Generate a data pipeline template based on the query"""
        return f"""import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging
from datetime import datetime
import json

class DataPipeline:
    """
    Data Pipeline for {query}
    Handles extraction, transformation, and loading of data
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pipeline_steps = []

    def extract_from_source(self, source_config: Dict[str, Any]) -> pd.DataFrame:
        """
        Extract data from source (database, API, file, etc.)
        """
        source_type = source_config.get('type', 'database')
        
        if source_type == 'database':
            import sqlalchemy
            engine = sqlalchemy.create_engine(source_config['connection_string'])
            df = pd.read_sql(source_config['query'], engine)
        elif source_type == 'api':
            import requests
            response = requests.get(source_config['url'], headers=source_config.get('headers', {{}}))
            data = response.json()
            df = pd.DataFrame(data)
        elif source_type == 'file':
            file_path = source_config['path']
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {{file_path}}")
        else:
            raise ValueError(f"Unsupported source type: {{source_type}}")
        
        self.logger.info(f"Extracted {{len(df)}} records from source")
        return df

    def transform_data(self, df: pd.DataFrame, transformations: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Apply transformations to the data
        """
        for transform in transformations:
            operation = transform['operation']
            
            if operation == 'rename_columns':
                df = df.rename(columns=transform['mapping'])
            elif operation == 'filter_rows':
                condition = transform['condition']
                df = df.query(condition)
            elif operation == 'add_column':
                col_name = transform['column_name']
                formula = transform['formula']
                df[col_name] = eval(formula)
            elif operation == 'drop_columns':
                df = df.drop(columns=transform['columns'])
            elif operation == 'fill_na':
                df = df.fillna(transform['value'])
            elif operation == 'normalize':
                columns = transform['columns']
                for col in columns:
                    df[col] = (df[col] - df[col].mean()) / df[col].std()
            else:
                self.logger.warning(f"Unknown transformation: {{operation}}")
        
        self.logger.info(f"Applied {{len(transformations)}} transformations")
        return df

    def load_to_destination(self, df: pd.DataFrame, destination_config: Dict[str, Any]):
        """
        Load transformed data to destination
        """
        dest_type = destination_config.get('type', 'database')
        
        if dest_type == 'database':
            import sqlalchemy
            engine = sqlalchemy.create_engine(destination_config['connection_string'])
            df.to_sql(
                destination_config['table_name'],
                engine,
                if_exists=destination_config.get('if_exists', 'replace'),
                index=destination_config.get('index', False)
            )
        elif dest_type == 'file':
            file_path = destination_config['path']
            if file_path.endswith('.csv'):
                df.to_csv(file_path, index=False)
            elif file_path.endswith('.json'):
                df.to_json(file_path, orient='records', date_format='iso')
            elif file_path.endswith('.parquet'):
                df.to_parquet(file_path, index=False)
        elif dest_type == 'api':
            import requests
            records = df.to_dict('records')
            for record in records:
                response = requests.post(
                    destination_config['url'],
                    json=record,
                    headers=destination_config.get('headers', {{}})
                )
                if response.status_code != 200:
                    self.logger.error(f"Failed to load record: {{response.text}}")
        else:
            raise ValueError(f"Unsupported destination type: {{dest_type}}")
        
        self.logger.info(f"Loaded {{len(df)}} records to destination")

    def run_pipeline(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the complete ETL pipeline
        """
        start_time = datetime.now()
        self.logger.info(f"Starting pipeline for {query}")
        
        try:
            # Extract
            extracted_df = self.extract_from_source(config['source'])
            
            # Transform
            transformed_df = self.transform_data(extracted_df, config['transformations'])
            
            # Load
            self.load_to_destination(transformed_df, config['destination'])
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {{
                'success': True,
                'records_processed': len(transformed_df),
                'duration_seconds': duration,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }}
            
            self.logger.info(f"Pipeline completed successfully: {{result}}")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {{
                'success': False,
                'error': str(e),
                'duration_seconds': duration,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }}
            
            self.logger.error(f"Pipeline failed: {{result}}")
            return result
"""
    
    def _generate_event_streaming_template(self, query: str, protocol: str, third_party_service: str, messaging_platform: str, params: Dict[str, Any]) -> str:
        """Generate an event streaming template based on the query"""
        if messaging_platform == "kafka":
            return f"""from kafka import KafkaProducer, KafkaConsumer
import json
from typing import Dict, Any, Callable
import threading
import logging
from datetime import datetime

class KafkaEventStreaming:
    """
    Kafka Event Streaming for {query}
    Handles publishing and consuming events
    """
    
    def __init__(self, bootstrap_servers: list = None):
        self.bootstrap_servers = bootstrap_servers or ['localhost:9092']
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda v: json.dumps(v).encode('utf-8') if v else None
        )
        self.consumers = {{}}
        self.logger = logging.getLogger(__name__)

    def publish_event(self, topic: str, event_data: Dict[str, Any], key: str = None) -> Dict[str, Any]:
        """
        Publish an event to a Kafka topic
        """
        try:
            future = self.producer.send(topic, value=event_data, key=key)
            record_metadata = future.get(timeout=10)
            
            result = {{
                'success': True,
                'topic': record_metadata.topic,
                'partition': record_metadata.partition,
                'offset': record_metadata.offset,
                'timestamp': datetime.fromtimestamp(record_metadata.timestamp / 1000.0).isoformat()
            }}
            
            self.logger.info(f"Event published to {{topic}}: {{result}}")
            return result
            
        except Exception as e:
            result = {{
                'success': False,
                'error': str(e)
            }}
            self.logger.error(f"Failed to publish event: {{result}}")
            return result

    def consume_events(self, topic: str, callback: Callable[[Dict[str, Any]], None], group_id: str = None):
        """
        Consume events from a Kafka topic
        """
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id or f'{{topic}}_consumer_group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
            auto_offset_reset='earliest'
        )
        
        self.consumers[topic] = consumer
        
        def consume_loop():
            for message in consumer:
                try:
                    event_data = message.value
                    self.logger.info(f"Received event from {{topic}}: {{event_data}}")
                    
                    # Call the provided callback with the event data
                    callback(event_data)
                    
                except Exception as e:
                    self.logger.error(f"Error processing message: {{e}}")
        
        # Run consumer in a separate thread
        consumer_thread = threading.Thread(target=consume_loop, daemon=True)
        consumer_thread.start()
        
        return consumer_thread

    def create_topic(self, topic_name: str, num_partitions: int = 1, replication_factor: int = 1):
        """
        Create a Kafka topic (requires admin client)
        """
        from kafka.admin import KafkaAdminClient, NewTopic
        
        admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        
        topic = NewTopic(
            name=topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor
        )
        
        try:
            admin_client.create_topics([topic], validate_only=False)
            self.logger.info(f"Topic {{topic_name}} created successfully")
            return {{'success': True, 'topic': topic_name}}
        except Exception as e:
            self.logger.error(f"Failed to create topic: {{e}}")
            return {{'success': False, 'error': str(e)}}
        finally:
            admin_client.close()

    def close(self):
        """
        Close the producer and all consumers
        """
        self.producer.close()
        for consumer in self.consumers.values():
            consumer.close()
"""
        else:
            return f"""# Event Streaming for {query}
# Messaging Platform: {messaging_platform}

# Generic event streaming implementation
import asyncio
import json
from typing import Dict, Any, Callable
import logging

class EventStreaming:
    """
    Event Streaming for {query}
    Handles publishing and consuming events
    """
    
    def __init__(self):
        self.topics = {{}}
        self.subscribers = {{}}
        self.logger = logging.getLogger(__name__)

    async def publish_event(self, topic: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish an event to a topic
        """
        if topic not in self.topics:
            self.topics[topic] = []
        
        event = {{
            'data': event_data,
            'timestamp': asyncio.get_event_loop().time(),
            'topic': topic
        }}
        
        self.topics[topic].append(event)
        
        # Notify subscribers
        if topic in self.subscribers:
            for subscriber in self.subscribers[topic]:
                try:
                    await subscriber(event)
                except Exception as e:
                    self.logger.error(f"Error in subscriber: {{e}}")
        
        return {{
            'success': True,
            'topic': topic,
            'event_id': len(self.topics[topic]) - 1
        }}

    def subscribe_to_topic(self, topic: str, callback: Callable[[Dict[str, Any]], None]):
        """
        Subscribe to a topic with a callback function
        """
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        
        self.subscribers[topic].append(callback)
        
        return {{
            'success': True,
            'topic': topic,
            'subscribed': True
        }}

    async def get_events(self, topic: str, count: int = 10) -> Dict[str, Any]:
        """
        Get events from a topic
        """
        if topic not in self.topics:
            return {{'events': [], 'count': 0}}
        
        events = self.topics[topic][-count:]
        return {{
            'events': events,
            'count': len(events),
            'total_in_topic': len(self.topics[topic])
        }}
"""
    
    def _generate_webhook_handler_template(self, query: str, protocol: str, third_party_service: str, messaging_platform: str, params: Dict[str, Any]) -> str:
        """Generate a webhook handler template based on the query"""
        return f"""from flask import Flask, request, jsonify
import hashlib
import hmac
import json
from typing import Dict, Any
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

class WebhookHandler:
    """
    Webhook Handler for {query}
    Handles incoming webhooks from third-party services
    """
    
    def __init__(self, webhook_secret: str = None):
        self.webhook_secret = webhook_secret or self._get_webhook_secret()
        self.handlers = {{}}
        self.logger = logger

    def _get_webhook_secret(self) -> str:
        """
        Retrieve webhook secret from environment
        """
        import os
        return os.getenv('WEBHOOK_SECRET', '')

    def verify_signature(self, payload: bytes, signature: str, algorithm: str = 'sha256') -> bool:
        """
        Verify the signature of the incoming webhook
        """
        if not self.webhook_secret:
            self.logger.warning("No webhook secret configured, skipping verification")
            return True
        
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload,
            getattr(hashlib, algorithm)
        ).hexdigest()
        
        # Compare signatures securely
        return hmac.compare_digest(
            f'{algorithm}={{expected_signature}}',
            signature
        )

    def register_handler(self, event_type: str, handler_func):
        """
        Register a handler function for a specific event type
        """
        self.handlers[event_type] = handler_func
        self.logger.info(f"Registered handler for event type: {{event_type}}")

    def handle_webhook(self, request) -> Dict[str, Any]:
        """
        Handle an incoming webhook request
        """
        # Get raw payload
        payload = request.get_data()
        signature = request.headers.get('X-Signature-256') or request.headers.get('X-Signature')
        
        # Verify signature if present
        if signature and not self.verify_signature(payload, signature):
            return {{
                'success': False,
                'error': 'Invalid signature'
            }}, 401
        
        try:
            # Parse JSON payload
            data = json.loads(payload.decode('utf-8'))
            
            # Determine event type
            event_type = (
                data.get('event_type') or 
                data.get('type') or 
                request.headers.get('X-Event-Type') or
                'unknown'
            )
            
            self.logger.info(f"Received webhook event: {{event_type}}")
            
            # Process event if handler exists
            if event_type in self.handlers:
                result = self.handlers[event_type](data)
                return {{
                    'success': True,
                    'event_type': event_type,
                    'processed': True,
                    'handler_result': result
                }}
            else:
                self.logger.warning(f"No handler registered for event type: {{event_type}}")
                return {{
                    'success': True,  # Still return success to acknowledge receipt
                    'event_type': event_type,
                    'processed': False,
                    'warning': f'No handler for event type: {{event_type}}'
                }}
                
        except json.JSONDecodeError:
            return {{
                'success': False,
                'error': 'Invalid JSON payload'
            }}, 400
        except Exception as e:
            self.logger.error(f"Error processing webhook: {{e}}")
            return {{
                'success': False,
                'error': str(e)
            }}, 500

# Example usage
webhook_handler = WebhookHandler()

# Define event handlers
def handle_payment_success(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle payment success event
    """
    transaction_id = data.get('transaction_id')
    amount = data.get('amount')
    
    # Process the successful payment
    # Update database, send notifications, etc.
    
    return {{
        'processed': True,
        'transaction_id': transaction_id,
        'action_taken': 'Payment processed successfully'
    }}

def handle_user_created(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle user creation event
    """
    user_id = data.get('user_id')
    email = data.get('email')
    
    # Perform actions when a new user is created
    # Send welcome email, create profile, etc.
    
    return {{
        'processed': True,
        'user_id': user_id,
        'action_taken': 'User setup completed'
    }}

# Register handlers
webhook_handler.register_handler('payment.success', handle_payment_success)
webhook_handler.register_handler('user.created', handle_user_created)

@app.route('/webhook', methods=['POST'])
def webhook_endpoint():
    """
    Webhook endpoint
    """
    result, status_code = webhook_handler.handle_webhook(request)
    return jsonify(result), status_code

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
"""
    
    def _generate_oauth_connector_template(self, query: str, protocol: str, third_party_service: str, messaging_platform: str, params: Dict[str, Any]) -> str:
        """Generate an OAuth connector template based on the query"""
        return f"""import requests
from urllib.parse import urlencode, parse_qs
import base64
import secrets
from typing import Dict, Any
import logging

class OAuthConnector:
    """
    OAuth Connector for {query}
    Handles OAuth 2.0 authentication flows
    """
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, 
                 authorize_url: str, token_url: str, scopes: list = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.authorize_url = authorize_url
        self.token_url = token_url
        self.scopes = scopes or []
        self.logger = logging.getLogger(__name__)

    def generate_auth_url(self, state: str = None) -> str:
        """
        Generate the authorization URL for the OAuth flow
        """
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {{
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.scopes),
            'state': state
        }}
        
        query_string = urlencode(params)
        auth_url = f'{{self.authorize_url}}?{{query_string}}'
        
        return auth_url

    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        """
        data = {{
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }}
        
        try:
            response = requests.post(
                self.token_url,
                data=data,
                headers={{'Accept': 'application/json'}}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return {{
                    'success': True,
                    'access_token': token_data.get('access_token'),
                    'refresh_token': token_data.get('refresh_token'),
                    'expires_in': token_data.get('expires_in'),
                    'token_type': token_data.get('token_type')
                }}
            else:
                return {{
                    'success': False,
                    'error': 'Failed to exchange code for token',
                    'error_description': response.text
                }}
        except Exception as e:
            return {{
                'success': False,
                'error': str(e)
            }}

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh the access token using the refresh token
        """
        data = {{
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token
        }}
        
        try:
            response = requests.post(
                self.token_url,
                data=data,
                headers={{'Accept': 'application/json'}}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return {{
                    'success': True,
                    'access_token': token_data.get('access_token'),
                    'refresh_token': token_data.get('refresh_token', refresh_token),
                    'expires_in': token_data.get('expires_in')
                }}
            else:
                return {{
                    'success': False,
                    'error': 'Failed to refresh token',
                    'error_description': response.text
                }}
        except Exception as e:
            return {{
                'success': False,
                'error': str(e)
            }}

    def make_authenticated_request(self, url: str, method: str = 'GET', 
                                 access_token: str = None, **kwargs) -> Dict[str, Any]:
        """
        Make an authenticated request to the API
        """
        if not access_token:
            return {{
                'success': False,
                'error': 'Access token required'
            }}
        
        headers = kwargs.pop('headers', {{}})
        headers['Authorization'] = f'Bearer {{access_token}}'
        
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            
            if response.status_code < 400:
                return {{
                    'success': True,
                    'data': response.json() if response.content else None,
                    'status_code': response.status_code
                }}
            else:
                return {{
                    'success': False,
                    'error': response.text,
                    'status_code': response.status_code
                }}
        except Exception as e:
            return {{
                'success': False,
                'error': str(e)
            }}

# Example implementation for a specific service
class {third_party_service.capitalize()}OAuthConnector(OAuthConnector):
    """
    OAuth Connector specifically for {third_party_service}
    """
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            authorize_url=f'https://{{third_party_service.lower()}}.com/oauth/authorize',
            token_url=f'https://{{third_party_service.lower()}}.com/oauth/token',
            scopes=['read', 'write']  # Adjust scopes as needed
        )

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from {third_party_service}
        """
        return self.make_authenticated_request(
            f'https://{{third_party_service.lower()}}.com/api/user',
            access_token=access_token
        )
"""
    
    def _generate_messaging_system_template(self, query: str, protocol: str, third_party_service: str, messaging_platform: str, params: Dict[str, Any]) -> str:
        """Generate a messaging system template based on the query"""
        if messaging_platform == "rabbitmq":
            return f"""import pika
import json
from typing import Dict, Any, Callable
import logging
import threading
from datetime import datetime

class RabbitMQMessaging:
    """
    RabbitMQ Messaging System for {query}
    Handles message queuing and pub/sub patterns
    """
    
    def __init__(self, connection_params: Dict[str, Any] = None):
        self.connection_params = connection_params or {{
            'host': 'localhost',
            'port': 5672,
            'virtual_host': '/',
            'credentials': pika.PlainCredentials('guest', 'guest')
        }}
        self.connection = None
        self.channel = None
        self.logger = logging.getLogger(__name__)
        self._connect()

    def _connect(self):
        """
        Establish connection to RabbitMQ
        """
        try:
            credentials = pika.PlainCredentials(
                self.connection_params['credentials']['username'], 
                self.connection_params['credentials']['password']
            )
            parameters = pika.ConnectionParameters(
                host=self.connection_params['host'],
                port=self.connection_params['port'],
                virtual_host=self.connection_params['virtual_host'],
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.logger.info("Connected to RabbitMQ")
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {{e}}")
            raise

    def declare_queue(self, queue_name: str, durable: bool = True):
        """
        Declare a queue
        """
        self.channel.queue_declare(queue=queue_name, durable=durable)
        self.logger.info(f"Declared queue: {{queue_name}}")

    def declare_exchange(self, exchange_name: str, exchange_type: str = 'direct', durable: bool = True):
        """
        Declare an exchange
        """
        self.channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=durable)
        self.logger.info(f"Declared exchange: {{exchange_name}}")

    def publish_message(self, queue_name: str = None, exchange_name: str = None, 
                       routing_key: str = '', message: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Publish a message to a queue or exchange
        """
        try:
            message_body = json.dumps(message)
            
            if queue_name:
                # Publish directly to queue
                self.channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=message_body,
                    properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
                )
            elif exchange_name:
                # Publish to exchange
                self.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key=routing_key,
                    body=message_body,
                    properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
                )
            else:
                return {{
                    'success': False,
                    'error': 'Either queue_name or exchange_name must be specified'
                }}
            
            result = {{
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'message_id': message.get('id', 'unknown')
            }}
            
            self.logger.info(f"Published message: {{result}}")
            return result
            
        except Exception as e:
            result = {{
                'success': False,
                'error': str(e)
            }}
            self.logger.error(f"Failed to publish message: {{result}}")
            return result

    def consume_messages(self, queue_name: str, callback: Callable[[str], None], 
                        auto_ack: bool = True):
        """
        Consume messages from a queue
        """
        def message_callback(ch, method, properties, body):
            try:
                message = json.loads(body.decode('utf-8'))
                self.logger.info(f"Received message from {{queue_name}}: {{message}}")
                
                # Process the message
                callback(message)
                
                if auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
            except Exception as e:
                self.logger.error(f"Error processing message: {{e}}")
                if not auto_ack:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=queue_name, on_message_callback=message_callback)
        
        def consume_loop():
            self.channel.start_consuming()
        
        # Run consumer in a separate thread
        consumer_thread = threading.Thread(target=consume_loop, daemon=True)
        consumer_thread.start()
        
        return consumer_thread

    def close_connection(self):
        """
        Close the RabbitMQ connection
        """
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            self.logger.info("Closed RabbitMQ connection")
"""
        else:
            return f"""# Messaging System for {query}
# Platform: {messaging_platform}

# Generic messaging system implementation
import asyncio
import json
from typing import Dict, Any, Callable
import logging

class MessagingSystem:
    """
    Messaging System for {query}
    Handles message queuing and pub/sub patterns
    """
    
    def __init__(self):
        self.queues = {{}}
        self.subscribers = {{}}
        self.logger = logging.getLogger(__name__)

    async def create_queue(self, queue_name: str):
        """
        Create a message queue
        """
        if queue_name not in self.queues:
            self.queues[queue_name] = []
            self.subscribers[queue_name] = []
            self.logger.info(f"Created queue: {{queue_name}}")
            return {{'success': True, 'queue': queue_name}}
        else:
            return {{'success': False, 'error': 'Queue already exists'}}

    async def send_message(self, queue_name: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to a queue
        """
        if queue_name not in self.queues:
            await self.create_queue(queue_name)
        
        # Add message to queue
        self.queues[queue_name].append(message)
        
        # Notify subscribers asynchronously
        if queue_name in self.subscribers:
            for subscriber in self.subscribers[queue_name]:
                try:
                    # Run subscriber in background
                    asyncio.create_task(subscriber(message))
                except Exception as e:
                    self.logger.error(f"Error in subscriber: {{e}}")
        
        return {{
            'success': True,
            'queue': queue_name,
            'message_id': len(self.queues[queue_name]) - 1
        }}

    def subscribe(self, queue_name: str, callback: Callable[[Dict[str, Any]], None]):
        """
        Subscribe to a queue with a callback function
        """
        if queue_name not in self.subscribers:
            self.subscribers[queue_name] = []
        
        self.subscribers[queue_name].append(callback)
        self.logger.info(f"Subscribed to queue: {{queue_name}}")
        
        return {{'success': True, 'queue': queue_name, 'subscribed': True}}

    async def get_messages(self, queue_name: str, count: int = 1) -> Dict[str, Any]:
        """
        Get messages from a queue (with basic FIFO implementation)
        """
        if queue_name not in self.queues:
            return {{'messages': [], 'count': 0}}
        
        messages = self.queues[queue_name][:count]
        # Remove retrieved messages
        self.queues[queue_name] = self.queues[queue_name][count:]
        
        return {{
            'messages': messages,
            'count': len(messages),
            'remaining_in_queue': len(self.queues[queue_name])
        }}
"""
    
    def _generate_generic_integration_code(self, query: str, integration_type: str, protocol: str, third_party_service: str, messaging_platform: str, params: Dict[str, Any]) -> str:
        """Generate generic integration code when specific type isn't determined"""
        return f"""# {integration_type.replace('_', ' ').title()} for {query}
# Protocol: {protocol}
# Third Party Service: {third_party_service}
# Messaging Platform: {messaging_platform}

# TODO: Implement the {integration_type.replace('_', ' ')} based on the requirements
"""

    async def _enhance_with_other_domains(self, generated_code: str, input_data: DomainInput) -> str:
        """Allow other domains to enhance the generated integration code"""
        # In a real implementation, this would coordinate with other domains
        # For now, we'll just return the original code
        return generated_code