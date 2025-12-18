from django.apps import AppConfig


class LoansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'loans'

    def ready(self):
        import sys
        from django.conf import settings
        import atexit
        import logging

        # Add backend directory to sys.path to allow importing common modules
        sys.path.append(str(settings.BASE_DIR.parent))

        try:
            from common.consul_client import ConsulClient
            from decouple import config

            logger = logging.getLogger(__name__)

            if not settings.DEBUG or config('REGISTER_CONSUL', default=False, cast=bool):
                 # Register service
                consul_client = ConsulClient(
                    host=settings.CONSUL_HOST,
                    port=settings.CONSUL_PORT
                )

                def deregister():
                    consul_client.deregister_service(settings.SERVICE_ID)

                if consul_client.register_service(
                    service_name=settings.SERVICE_NAME,
                    service_id=settings.SERVICE_ID,
                    address=settings.SERVICE_ADDRESS,
                    port=settings.SERVICE_PORT,
                    tags=settings.SERVICE_TAGS
                ):
                    atexit.register(deregister)
            else:
                logger.info("Skipping Consul registration in DEBUG mode (set REGISTER_CONSUL=True to enable)")

        except ImportError:
            pass
        except Exception as e:
            # We don't want to break startup if consul fails
            pass
