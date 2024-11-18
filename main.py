import gradio as gr
from kubernetes import client, config

# Charger la configuration du kubeconfig (nécessaire si vous avez un fichier kubeconfig local)
config.load_kube_config()  # Si vous êtes en local. Sinon, utilisez load_incluster_config() si dans un pod Kubernetes.

def get_namespaces():
    """
    Récupère tous les namespaces dans le cluster Kubernetes.
    """
    v1 = client.CoreV1Api()
    namespaces = v1.list_namespace()
    
    namespace_names = [namespace.metadata.name for namespace in namespaces.items]
    return namespace_names

def get_pods(namespace):
    """
    Récupère les pods en cours d'exécution dans le namespace donné.
    """
    if namespace is None:
        namespace="default"

    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace)
    
    pod_names = [pod.metadata.name for pod in pods.items]
    return "\n".join(pod_names)

def get_deployments(namespace):
    """
    Récupère les deployments et leur nombre de réplicas dans le namespace donné.
    """
    if namespace is None:
        namespace = "default"

    config.load_kube_config()
    apps_v1 = client.AppsV1Api()
    deployments = apps_v1.list_namespaced_deployment(namespace)

    deployment_info = []
    for deployment in deployments.items:
        deployment_name = deployment.metadata.name
        replica_count = deployment.spec.replicas
        deployment_info.append(f"{deployment_name}:{replica_count}")

    return "\n".join(deployment_info)

def get_unsynced_argo_cd_apps(namespace="argo-cd"):
    # Charger la configuration du cluster Kubernetes (locale ou incluse dans un Pod)
    config.load_kube_config()  # Utilisez config.load_incluster_config() si vous êtes dans un Pod

    # Configurer l'API CustomObjects
    custom_api = client.CustomObjectsApi()

    # Récupérer les applications Argo CD (group, version, plural)
    group = "argoproj.io"
    version = "v1alpha1"
    plural = "applications"

    # Liste les applications dans le namespace donné
    try:
        apps = custom_api.list_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural
        )

        # Filtrer les applications non-synchronisées
        synced_apps = [
            app for app in apps["items"]
            if app.get("status", {}).get("sync", {}).get("status") != "Synced"
        ]
        result = [app['metadata']['name'] for app in synced_apps]
        result.sort
        return "\n".join(result)

    except client.exceptions.ApiException as e:
        print(f"Erreur lors de la récupération des applications : {e}")
        return []

def get_synced_argo_cd_apps(namespace="argo-cd"):
    # Charger la configuration du cluster Kubernetes (locale ou incluse dans un Pod)
    config.load_kube_config()  # Utilisez config.load_incluster_config() si vous êtes dans un Pod

    # Configurer l'API CustomObjects
    custom_api = client.CustomObjectsApi()

    # Récupérer les applications Argo CD (group, version, plural)
    group = "argoproj.io"
    version = "v1alpha1"
    plural = "applications"

    # Liste les applications dans le namespace donné
    try:
        apps = custom_api.list_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural
        )

        # Filtrer les applications non-synchronisées
        synced_apps = [
            app for app in apps["items"]
            if app.get("status", {}).get("sync", {}).get("status") == "Synced"
        ]

        result = [app['metadata']['name'] for app in synced_apps]
        result.sort
        return "\n".join(result)

    except client.exceptions.ApiException as e:
        print(f"Erreur lors de la récupération des applications : {e}")
        return []

def remove_duplicates(lst):
    return list(set(lst))

def get_argo_cd_namespace(namespace="argo-cd"):
    # Charger la configuration du cluster Kubernetes (locale ou incluse dans un Pod)
    config.load_kube_config()  # Utilisez config.load_incluster_config() si vous êtes dans un Pod

    # Configurer l'API CustomObjects
    custom_api = client.CustomObjectsApi()

    # Récupérer les applications Argo CD (group, version, plural)
    group = "argoproj.io"
    version = "v1alpha1"
    plural = "applications"

    # Liste les applications dans le namespace donné
    try:
        apps = custom_api.list_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural
        )

        # Filtrer les applications non-synchronisées
        synced_apps = [
            app for app in apps["items"]
            if app.get("status", {}).get("sync", {}).get("status") == "Synced"
        ]

        result = [app['spec']['destination']['namespace'] for app in synced_apps]
        ma_liste_sans_doublons = remove_duplicates(result)
        ma_liste_sans_doublons.sort(key=str.lower)

        # ma_liste_sans_doublons.sort
        return "\n".join(ma_liste_sans_doublons)

    except client.exceptions.ApiException as e:
        print(f"Erreur lors de la récupération des applications : {e}")
        return []
    
def get_statefulsets(namespace):
    """
    Récupère les StatefulSets et leur nombre de réplicas dans le namespace donné.
    """
    if namespace is None:
        namespace = "default"

    config.load_kube_config()
    apps_v1 = client.AppsV1Api()
    statefulsets = apps_v1.list_namespaced_stateful_set(namespace)

    statefulset_info = []
    for statefulset in statefulsets.items:
        statefulset_name = statefulset.metadata.name
        replica_count = statefulset.spec.replicas
        statefulset_info.append(f"{statefulset_name}:{replica_count}")

    return "\n".join(statefulset_info)

def string_to_markdown_table(input_string):
    lines = input_string.strip().split('\n')
    header = lines[0].split(':')
    rows = [line.split(':') for line in lines[1:]]
    
    # Calcul de la largeur maximale de chaque colonne
    column_widths = [max(len(str(row[i])) for row in [header] + rows) for i in range(len(header))]
    
    # Formatage de l'en-tête
    header_line = '| ' + ' | '.join(cell.ljust(width) for cell, width in zip(header, column_widths)) + ' |'
    separator_line = '|-' + '-|-'.join('-' * width for width in column_widths) + '-|'
    
    # Formatage des lignes du tableau
    row_lines = ['| ' + ' | '.join(cell.ljust(width) for cell, width in zip(row, column_widths)) + ' |' for row in rows]
    
    # Assemblage du tableau Markdown
    table = '\n'.join([header_line, separator_line] + row_lines)
    
    return table

def count_replicas_per_namespace(namespace):
    config.load_kube_config()
    api_instance = client.AppsV1Api()

    deployments = api_instance.list_namespaced_deployment(namespace)
    stateful_sets = api_instance.list_namespaced_stateful_set(namespace)

    total_replicas = 0

    for deployment in deployments.items:
        total_replicas += deployment.spec.replicas

    for stateful_set in stateful_sets.items:
        total_replicas += stateful_set.spec.replicas

    return total_replicas

def scale_down(namespace):
    # Charger la configuration kubeconfig
    config.load_kube_config()

    # Créer un client pour les apps/v1
    api_instance = client.AppsV1Api()

    # Récupérer la liste des Deployments pour la namespace donnée
    deployments = api_instance.list_namespaced_deployment(namespace)

    # Scaler à 0 les replicas de chaque Deployment
    for deployment in deployments.items:
        deployment.spec.replicas = 0
        api_instance.replace_namespaced_deployment(deployment.metadata.name, namespace, deployment)
        print(f"Deployment {deployment.metadata.name} scaled down to 0 replicas")

    # Récupérer la liste des StatefulSets pour la namespace donnée
    stateful_sets = api_instance.list_namespaced_stateful_set(namespace)

    # Scaler à 0 les replicas de chaque StatefulSet
    for stateful_set in stateful_sets.items:
        stateful_set.spec.replicas = 0
        api_instance.replace_namespaced_stateful_set(stateful_set.metadata.name, namespace, stateful_set)
        print(f"StatefulSet {stateful_set.metadata.name} scaled down to 0 replicas")

# scale_down("geek-cookbook")

with gr.Blocks() as demo:
    # Titre principal
    gr.Markdown("## Exemple Gradio avec Colonne et Bloc")
    
    
    with gr.Row():
        gr.Image("logo.jpg", scale=2, show_fullscreen_button=False,show_download_button=False)
    
    with gr.Row():
        gr.Interface(
            fn=get_synced_argo_cd_apps,  # Fonction pour récupérer les pods
            inputs=[],
            outputs=[
                gr.Textbox(label="Apps Sync"),  # Output pour afficher les pods
            ],
            live=True,  # Actualiser en temps réel si nécessaire
            flagging_mode='never', # Désactive complètement le flagging
            # clear_input=False, # Désactive le bouton "Clear"            
        )
    with gr.Row():
        gr.Interface(
            fn=get_unsynced_argo_cd_apps,  # Fonction pour récupérer les pods
            inputs=[],
            outputs=[
                gr.Textbox(label="Apps Unsync"),  # Output pour afficher les pods
            ],
            live=True, # Actualiser en temps réel si nécessaire
            flagging_mode='never', # Désactive complètement le flagging
            # clear_input=False, # Désactive le bouton "Clear"
        )   

    with gr.Row():
        gr.Interface(
            fn=get_deployments, 
            inputs=[],
            outputs=[
                gr.Textbox(label="Deployments"),  # Output pour afficher les pods
            ],
            live=True, # Actualiser en temps réel si nécessaire
            flagging_mode='never', # Désactive complètement le flagging
            # clear_input=False, # Désactive le bouton "Clear"
        )   

    # with gr.Row():
    #     gr.Interface(
    #         fn=get_statefulsets, 
    #         inputs=[],
    #         outputs=[
    #             gr.Textbox(label="Statefulsets"),  # Output pour afficher les pods
    #         ],
    #         live=True, # Actualiser en temps réel si nécessaire
    #         allow_flagging=False, # Désactive les boutons de flagging
    #         show_api=False, # Cache l'onglet API
    #     )   

    with gr.Row():
        gr.Interface(
            fn=get_statefulsets, 
            inputs=[],
            outputs=[
                gr.Textbox(label="Statefulsets"),  # Output pour afficher les pods
            ],
            live=True, # Actualiser en temps réel si nécessaire
            flagging_mode='never', # Désactive complètement le flagging
            # clear_input=False, # Désactive le bouton "Clear"
        )
    with gr.Row():
        gr.Markdown("Unsync Apps")
        gr.Markdown(string_to_markdown_table(get_unsynced_argo_cd_apps("")))
    with gr.Row():
        gr.Markdown("Sync Apps")
        gr.Markdown(string_to_markdown_table(get_synced_argo_cd_apps("")))        
    with gr.Row():
        gr.Markdown("Apps destination Namespace")
        gr.Markdown(string_to_markdown_table(get_argo_cd_namespace("")))        

namespaces=get_argo_cd_namespace("").split("\n")
for namespace in namespaces:
    replica_count = count_replicas_per_namespace(namespace)
    print(f"Total replicas in namespace '{namespace}': {replica_count}")

# Lancer l'application
demo.launch()