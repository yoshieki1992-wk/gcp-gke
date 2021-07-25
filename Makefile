SHELL:=/bin/bash


all: HELP MANAGE_CREDENTIALS GENERATE_APP GENERATE_IMAGE CREATE_CLUSTER VIEW_OUTPUTS  

HELP:
	@echo -e "OPCIONES \n-----------------------------------------------------\n make MANAGE_CREDENTIALS: Configuracion de credenciales\n make GENERATE_APP: Generar api flask directorio y archivos \n make GENERATE_IMAGE: Build/push docker image \n make CREATE_CLUSTER: GKE pulumi code\n make VIEW_OUTPUTS: Visualizar outputs y validar endpoints \n make DESTROY: Destroy all resources \n -----------------------------------------------------\n"

VALIDATE:
	@chmod +x scripts/export_credentials \
		  gke/create_cluster \
		  scripts/create_app \
                  scripts/create_container_image \
		  scripts/outputs \
 		  scripts/destroy

MANAGE_CREDENTIALS:
	@source scripts/./export_credentials
	
GENERATE_APP:
	@source scripts/./create_app

GENERATE_IMAGE:
	@source scripts/./create_container_image

CREATE_CLUSTER:
	@source scripts/./create_cluster

VIEW_OUTPUTS:
	@source scripts/./outputs

DESTROY: 
	@source scripts/./destroy
