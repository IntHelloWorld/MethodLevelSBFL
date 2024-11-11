import os
import shutil
import subprocess as sp
import time
from pathlib import Path

logDir = 'logs'

maxProcessNum = 8
processPool = []  # storing (process, "pid-bid")

def waitPatchPoolFinish():
    while (len(processPool) > 0):
        time.sleep(1)
        valuesToRemove = []
        for process, projId in processPool:
            exitCode = process.poll()
            if exitCode is None:
                continue
            else:
                if exitCode != 0:
                    print('[ERROR] process {} finished with non-zero exit code!'.format(projId))
                valuesToRemove.append((process, projId))
                print('===== Finished {} ====='.format(projId))
        for value in valuesToRemove:
            processPool.remove(value)

def runGz(pid: str, bid: str, sid: str):
    while (len(processPool) >= maxProcessNum):
        time.sleep(1)
        valuesToRemove = []
        for process, projId in processPool:
            exitCode = process.poll()
            if exitCode is None:
                continue
            else:
                if exitCode != 0:
                    print('[ERROR] process {} finished with non-zero exit code!'.format(projId))
                valuesToRemove.append((process, projId))
                print('===== Finished {} ====='.format(projId))
        for value in valuesToRemove:
            processPool.remove(value)
    logPath = os.path.join(logDir, pid+'-'+bid+'.log')
    with open(logPath, 'w') as f:
        if pid in ["Qpid_client", "Appformer_uberfire_workbench_client"]:
            process = sp.Popen("bash runGz_GrowingBugs_long_classpath.sh {} {} {}".format(pid, bid, sid), stdout=f, stderr=f, shell=True, universal_newlines=True)
        else:
            process = sp.Popen("bash runGz_GrowingBugs.sh {} {} {}".format(pid, bid, sid), stdout=f, stderr=f, shell=True, universal_newlines=True)
        # process = sp.Popen("echo {}-{}".format(pid, bid), stdout=f, stderr=f, shell=True, universal_newlines=True)
    processPool.append((process, pid + '-' + bid))
    print('===== Start {}-{} ====='.format(pid, bid))

d4j140ProjNames = ['Chart', 'Closure', 'Lang', 'Math', 'Mockito', 'Time']

def getD4jProjNameFromSimpleName(simpleName):
    for projName in d4j140ProjNames:
        if simpleName == projName.lower():
            return projName
    print('Cannot find the project name for the simple name: {}'.format(simpleName))
    exit -1

# projDict = {
#     'IO': (list(range(1, 32)), [4, 7, 19, 20, 21, 23, 24, 26, 28], "None"),
#     'Validator': (list(range(1, 26)), [3, 5, 10, 12], "None"),
#     'Pool': (list(range(1, 31)), [2, 3, 4, 8, 9, 15, 17, 18, 19, 22, 23, 25, 28], "None"),
#     'Javapoet': (list(range(1, 18)), [], "None"),
#     'Zip4j': (list(range(1, 53)), [], "None"),
#     'Spoon': (list(range(1, 18)), [], "None"),
#     'Markedj': (list(range(1, 18)), [], "None"),
#     'Dagger_core': (list(range(1, 21)), [], "core"),
# }

# projDict = {
#     'Tika_core': (list(range(4, 5)), [], "tika-core"),
# }

projDict = {
    'AaltoXml': ([1, 2, 3, 4, 5, 7, 8, 9], [], 'None'),
    'Bcel': ([1, 2, 3, 4, 5, 6], [], 'None'),
    'Ber_tlv': ([1, 2, 3, 4], [], 'None'),
    'Burst': ([1, 2, 3], [], 'burst'),
    'Canvas_api': ([1, 2, 3, 4], [], 'None'),
    'Chart': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26], [], 'None'),
    'Cli': ([1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42], [], 'None'),
    'Closure': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176], [], 'None'),
    'Codec': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], [], 'None'),
    'Collections': ([25, 26, 27, 28, 29, 30, 31, 35], [], 'None'),
    'Commons_suncalc': ([1, 2], [], 'None'),
    'Compress': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 50, 52, 53], [], 'None'),
    'Coveralls_maven_plugin': ([1, 2, 3, 4, 5, 6, 7, 8], [], 'None'),
    'Csv': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], [], 'None'),
    'Dbutils': ([1, 2], [], 'None'),
    'Deltaspike_api': ([1, 2, 3, 4, 5, 6], [], 'deltaspike/core/api'),
    'Disklrucache': ([1, 2, 3, 4, 5, 6], [], 'None'),
    'Docker_java_api': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [], 'None'),
    'Drools_model_compiler': ([1], [], 'drools-model/drools-model-compiler'),
    'Email': ([3, 4, 5], [], 'None'),
    'Functor': ([1, 2], [], 'None'),
    'Geo': ([1, 2, 3], [], 'geo'),
    'Geometry_core': ([1, 3], [], 'commons-geometry-core'),
    'Github_release_plugin': ([1, 2], [], 'None'),
    'Graph': ([1, 2, 3, 4, 5], [], 'None'),
    'Gson': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25], [], 'gson'),
    'Hivemall_core': ([1, 2, 3], [], 'core'),
    'IO': ([1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 22, 25, 27, 29, 30, 31], [], 'None'),
    'Imaging': ([1, 3, 4, 5, 6, 7, 8, 10, 11, 14], [], 'None'),
    'Jackrabbit_filevault_vault_core': ([1], [], 'vault-core'),
    'Jackrabbit_filevault_vault_validation': ([1, 2, 3, 4], [], 'vault-validation'),
    'JacksonCore': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28, 29, 30, 31], [], 'None'),
    'JacksonDatabind': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 121, 122, 123, 124, 125, 126, 128, 129, 131, 132, 133, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156], [], 'None'),
    'JacksonDataformatBinary_cbor': ([1, 2, 3, 4, 5], [], 'cbor'),
    'JacksonDataformatBinary_protobuf': ([1, 2, 3, 4], [], 'protobuf'),
    'JacksonXml': ([1, 2, 3, 4, 5, 6], [], 'None'),
    'James_mime4j_core': ([1, 2, 3, 4, 5, 6, 7, 8, 9], [], 'core'),
    'Lang': ([1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 69, 71, 73, 76, 80, 81, 82, 83, 84], [], 'None'),
    'Math': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35], [], 'None'),
    'Mockito': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], [], 'None'),
    'Shiro_web': ([1, 3, 7, 8, 9, 10, 11, 12], [], 'web'),
    'Time': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26, 27], [], 'None'),
    'Deft': ([1], [], 'None'),
    'Dosgi_common': ([1, 2], [], 'common'),
    'Doubleclick_core': ([1], [], 'doubleclick-core'),
    # 'Doxia_module_apt': ([1, 2], [], 'doxia-modules/doxia-module-apt'), # checked
    'Drools_traits': ([1], [], 'drools-traits'),
    'Dropwizard_spring': ([1], [], 'None'),
    # 'Farm': ([1, 2, 3, 4], [], 'None'), # checked
    'Flume_ngcore': ([1, 2], [], 'flume-ng-core'),
    'Fluo_api': ([1, 3], [], 'modules/api'),
    'Hbase_common': ([1], [], 'hbase-common'),
    'Hierarchical_clustering_java': ([1], [], 'None'),
    'Hilbert_curve': ([1, 2, 3], [], 'None'),
    'Hive_funnel_udf': ([1], [], 'None'),
    'Hono_client': ([1, 2, 3, 4], [], 'client'),
    'Httpcomponents_core_h2': ([1], [], 'httpcore5-h2'),
    'Httpcomponents_core_httpcore5': ([1, 2, 3], [], 'httpcore5'),
    'JXR': ([1], [], 'None'),
    'Jsoup': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93], [], 'None'),
    'JxPath': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22], [], 'None'),
    # 'Math_4j': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106], [], 'None'),
    'MShade': ([1, 2, 3, 4, 6, 7], [1, 3, 7], 'None'), # checked
    'Tika': ([1, 2, 5, 6, 7], [], 'None'),
    'Validator': ([1, 2, 4, 6, 7, 8, 9, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25], [], 'None'),
    # 'Pool': ([1, 5, 6, 7, 10, 11, 12, 13, 14, 16, 20, 21, 24, 26, 27, 29, 30], [], 'None'), # checked
    # 'Net': ([9, 10, 12, 14, 15, 16, 17, 18, 20, 21, 23, 24, 25, 26], [], 'None'), # checked
    'Numbers_angle': ([1, 2], [], 'commons-numbers-angle'),
    'MGpg': ([1], [], 'None'),
    'Text': ([1, 2, 4, 5], [], 'None'),
    'Tika_core': ([4, 6, 9, 11, 17, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39], [17, 20, 33, 38, 39], 'tika-core'), # checked
    'Tika_app': ([1, 3], [], 'tika-app'),
    'Shiro_core': ([37, 40, 46, 52, 98, 144, 176, 181, 202, 203], [], 'core'),
    # 'Jena_core': ([2], [], 'jena-core'), # checked
    # 'MDeploy': ([1], [], 'None'), # checked
    'Jackrabbit_oak_core': ([1, 2, 3, 4, 5], [], 'oak-core'),
    'Maven_checkstyle_plugin': ([1], [], 'None'),
    'James_project_core': ([1, 2], [], 'core'),
    'Pdfbox_fontbox': ([1, 2, 3, 4, 5, 6, 7], [], 'fontbox'),
    'HttpClient5': ([1, 2, 4, 5, 6, 7, 8], [], 'httpclient5'),
    'jackson_modules_java8_datetime': ([1, 2, 3, 4, 5], [], 'datetime'),
    'Pdfbox_pdfbox': ([1, 2, 3], [], 'pdfbox'),
    'Storm_client': ([1], [], 'storm-client'),
    'JacksonDataformatsText_yaml': ([1, 2, 4, 5, 6, 7], [], 'yaml'),
    'JacksonDataformatsText_properties': ([1, 2], [], 'properties'),
    'JacksonDataformatBinary_avro': ([1, 2], [], 'avro'),
    'JavaClassmate': ([1, 2], [], 'None'),
    'JacksonModuleJsonSchema': ([1], [], 'None'),
    'JacksonDatatypeJoda': ([2, 3], [], 'None'),
    'JacksonDatatypeJsr310': ([1, 2, 3, 4], [], 'None'),
    'JacksonDataformatBinary_smile': ([1, 2, 3], [], 'smile'),
    'JacksonModuleAfterburner': ([1, 2, 3], [], 'None'),
    'Woodstox': ([1, 2, 3, 4, 5, 6, 7], [], 'None'),
    'MetaModel_core': ([1, 2, 3, 4, 5, 6, 7, 8, 9], [7], 'core'), # checked
    'MetaModel_csv': ([1], [], 'csv'),
    'MetaModel_excel': ([1], [], 'excel'),
    'MetaModel_jdbc': ([1, 2, 3], [], 'jdbc'),
    'MetaModel_pojo': ([1], [], 'pojo'),
    'MetaModel_salesforce': ([1], [], 'salesforce'),
    'Wink_common': ([1, 2, 3, 4], [], 'wink-common'),
    'Xbean_naming': ([1], [], 'xbean-naming'),
    'James_project_server_container_core': ([1], [], 'server/container/core'),
    'Johnzon_core': ([1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12], [], 'johnzon-core'),
    'Nifi_mock': ([1, 2], [], 'nifi-mock'),
    'Rat_core': ([1], [], 'apache-rat-core'),
    'Rat_plugin': ([1], [], 'apache-rat-plugin'),
    'Tez_common': ([1], [], 'tez-common'),
    'Tinkerpop_gremlin_core': ([1], [], 'gremlin-core'),
    'Webbeans_web': ([1], [], 'webbeans-web'),
    'Johnzon_jsonb': ([1, 2, 3, 4, 5, 6], [], 'johnzon-jsonb'),
    'Johnzon_jaxrs': ([1], [], 'johnzon-jaxrs'),
    'Incubator_tamaya_api': ([1, 2], [], 'code/api'),
    'James_project_mailet_standard': ([1], [], 'mailet/standard'),
    'Johnzon_jsonschema': ([1, 2], [], 'johnzon-jsonschema'),
    'Johnzon_mapper': ([1, 2, 3, 4, 5, 6], [], 'johnzon-mapper'),
    'Karaf_main': ([1], [], 'main'),
    'Appformer_uberfire_commons_editor_backend': ([1], [], 'uberfire-extensions/uberfire-commons-editor/uberfire-commons-editor-backend'),
    'Kie_pmml_commons': ([1, 2, 3], [], 'kie-pmml-trusty/kie-pmml-commons'),
    'Kie_memory_compiler': ([1], [], 'kie-memory-compiler'),
    'Jbpm_human_task_workitems': ([1], [], 'jbpm-human-task/jbpm-human-task-workitems'),
    'Appformer_uberfire_security_management_client': ([1], [], 'uberfire-extensions/uberfire-security/uberfire-security-management/uberfire-security-management-client'),
    # 'Appformer_uberfire_workbench_client': ([1, 2, 3], [], 'uberfire-workbench/uberfire-workbench-client'), # checked
    'Jandex': ([1, 2, 3, 4, 5, 6], [], 'None'),
    'Kogito_editors_java_kie_wb_common_stunner_widgets': ([1], [], 'kie-wb-common-stunner/kie-wb-common-stunner-client/kie-wb-common-stunner-widgets'),
    'Ognl': ([1], [], 'None'),
    'Qpid_client': ([1, 2, 3, 4, 5, 6, 7, 8], [7], 'qpid-jms-client'), # checked
    'Switchyard_admin': ([1], [], 'admin'),
    'Weld_se_core': ([1], [], 'environments/se/core'),
    'Jboss_modules': ([1, 3, 4, 5, 6], [], 'None'),
    'Jboss_threads': ([1], [], 'None'),
    'Minaftp_api': ([1], [], 'ftplet-api'),
    'Sling_validation': ([1], [], 'None'),
    'Switchyard_config': ([1], [], 'config'),
    'Switchyard_validate': ([1], [], 'validate'),
    'Wildfly_naming_client': ([1, 2], [], 'None'),
    'Knox_assertion_common': ([1], [], 'gateway-provider-identity-assertion-common'),
    'Oozie_client': ([1, 2], [], 'client'),
    'Qpidjms_client': ([1, 2, 3], [], 'client'),
    'Rdf4j_query': ([1], [], 'core/query'),
    'Rdf4j_rio_api': ([1, 2], [], 'core/rio/api'),
    'Rdf4j_rio_jsonld': ([1, 2], [], 'core/rio/jsonld'),
    'Rdf4j_rio_rdfjson': ([1, 2], [], 'core/rio/rdfjson'),
    'Rdf4j_rio_rdfxml': ([1], [], 'core/rio/rdfxml'),
    'Rdf4j_rio_turtle': ([1, 2, 3, 4, 6, 8, 9, 10], [], 'core/rio/turtle'),
    'Sentry_ccommon': ([1, 2], [], 'sentry-core/sentry-core-common'),
    'Sling_apiregions': ([1, 2, 3], [], 'None'),
    'Sling_cpconverter': ([1, 2, 3], [], 'None'),
    'Tiles_api': ([1, 2], [], 'tiles-api'),
    'Tiles_core': ([1, 2, 3], [], 'tiles-core'),
    'Twill_dcore': ([1], [], 'twill-discovery-core'),
    # 'Maven2_artifact': ([1, 2], [], 'maven-artifact'), # checked
    # 'Maven2_project': ([1, 2], [], 'maven-project'), # checked
    'Wicket_request': ([1, 2, 3, 4, 5, 6], [], 'wicket-request'),
    'Cayenne_xmpp': ([1], [], 'cayenne-xmpp'),
    'Wicket_util': ([1, 2, 3, 4], [], 'wicket-util'),
    'Wicket_spring': ([1], [], 'wicket-spring'),
    'Cayenne_jgroups': ([1], [], 'cayenne-jgroups'),
    'Cayenne_jms': ([1], [], 'cayenne-jms'),
    'Struts1_core': ([1, 2], [], 'core'),
    'Wicket_cdi': ([1], [], 'wicket-cdi'),
    'Wicket_core': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18], [], 'wicket-core'),
    'Mshared_archiver': ([1], [], 'maven-archiver'),
    'Shindig_common': ([1], [], 'java/common'),
    'Xbean_reflect': ([1], [], 'xbean-reflect'),
    'Mrunit': ([1, 2], [], 'None'),
    'Rave_core': ([1, 2], [], 'rave-components/rave-core'),
    'Rave_commons': ([1], [], 'rave-components/rave-commons'),
    'Rave_web': ([1], [], 'rave-components/rave-web'),
    'Jmh_core': ([1], [], 'jmh-core'),
    'Sdk_core': ([1, 2, 3], [2, 3], 'None'), # checked
    'Cargo_container': ([1, 2, 3, 4], [4], 'core/api/container'), # checked
    'Oak_commons': ([1], [], 'oak-commons'),
    'Streamex': ([1, 2, 3, 4, 5, 6, 7], [], 'None'),
    'Javapoet': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], [], 'None'),
    'RTree': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [8], 'None'), # checked
    'Spoon': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], [], 'None'),
    'Slack_java_webhook': ([1], [], 'None'),
    'Zip4j': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52], [], 'None'),
    'Incubator_retired_pirk': ([1], [], 'None'),
    'Sparsebitset': ([1, 2], [], 'None'),
    'Assertj_assertions_generator': ([1, 2, 3, 4, 5, 6, 7], [], 'None'),
    'Config_magic': ([2], [], 'None'),
    'Jcodemodel': ([1, 2, 3, 4, 5, 6, 7], [], 'None'),
    'Jdbm3': ([1, 2, 3, 4, 5, 6], [], 'None'),
    'Mybatis_pagehelper': ([1, 2, 3, 4], [], 'None'),
    'N5': ([1, 2], [], 'None'),
    'Stash_jenkins_postreceive_webhook': ([1], [], 'None'),
    'Suffixtree': ([1], [], 'None'),
    'Template_benchmark': ([1], [], 'None'),
    'Vectorz': ([1, 2, 3, 4, 5, 6], [], 'None'),
    'Cli_parser': ([1], [], 'None'),
    'Gatling_report': ([1, 2, 3], [], 'None'),
    'Semux_core': ([3], [], 'None'),
    'Solarpositioning': ([1, 2, 3], [], 'None'),
    'Sparkey_java': ([1, 2, 3], [], 'None'),
    'Shazamcrest': ([1, 2], [], 'None'),
    'Restfixture': ([1, 2, 3, 4], [], 'None'),
    'Chronicle_network': ([1, 2, 3, 4], [], 'None'),
    'Gocd_slack_build_notifier': ([1, 2, 3], [], 'None'),
    'Confluence_http_authenticator': ([1], [], 'None'),
    'Tempus_fugit': ([1], [], 'None'),
    'Kafka_graphite': ([1], [], 'None'),
    'Simple_excel': ([1], [], 'None'),
    'Trident_ml': ([1], [], 'None'),
    'Tascalate_concurrent': ([1, 2], [], 'None'),
    'Jcabi_github': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82], [82], 'None'),
    'Podam': ([1], [], 'None'),
    'Sansorm': ([1, 2, 3, 4, 5, 6, 7], [3], 'None'), # checked
    'Transmittable_thread_local': ([1, 2, 3, 4], [], 'None'),
    'Jchronic': ([1], [], 'None'),
    'Netconf_java': ([1], [], 'None'),
    'Xades4j': ([1, 2, 3, 4], [], 'None'),
    'Spatial4j': ([1, 2, 3, 4], [], 'None'),
    'Iciql': ([1, 2], [], 'None'),
    'Metrics_opentsdb': ([1, 2], [], 'None'),
    'Spring_context_support': ([2], [], 'None'),
    'Jmimemagic': ([1], [], 'None'),
    'Markedj': ([1, 2], [], 'None'),
    'Sonartsplugin': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [], 'None'),
    'Aws_maven': ([1], [], 'None'),
    'Snomed_owl_toolkit': ([1, 2], [], 'None'),
    'Weak_lock_free': ([1], [], 'None'),
    'Proj4J': ([1, 2, 3, 4, 5, 6, 7, 8, 9], [], 'None'),
    'Rocketmq_mqtt_ds': ([1], [], 'mqtt-ds'),
    'Retrofit': ([1, 2, 3], [], 'retrofit'),
    'Jnagmp': ([1], [], 'jnagmp'),
    'Rocketmq_mqtt_cs': ([1], [], 'mqtt-cs'),
    'Dagger_core': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], [], 'core'),
    'Google_java_format_core': ([1], [], 'core'),
    'Jimfs': ([1, 2], [], 'jimfs'),
    'Open_location_code_java': ([1, 2, 3, 4], [], 'java'),
    'Gwtmockito': ([1, 2, 3], [], 'gwtmockito'),
    'Render_app': ([1, 2, 3, 4, 5], [], 'render-app'),
    'Tape': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [], 'tape'),
    'Jcabi_http': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], [], 'None'),
    'Jcabi_aether': ([1], [], 'None'),
    'Jcabi_w3c': ([1], [], 'None'),
    'Jcabi_email': ([1, 2, 3, 4], [], 'None'),
    'Jcabi_log': ([1, 2, 3, 4, 5, 6, 7, 8, 9], [], 'None'),
    'Jcabi_matchers': ([1, 2], [], 'None'),
    'Jfreechart_fse': ([1, 2], [], 'None'),
    'Jfreesvg': ([1], [], 'None'),
    'Leshan_core': ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [], 'leshan-core'),
    'Rdf_jena': ([1], [], 'commons-rdf-jena'),
    'Jackson_annotations': ([1], [], 'None'),
    # 'Jackson_datatype_hibernate4': ([1], [], 'hibernate4'), # checked
    'Rtree2': ([1, 2, 3, 4, 5, 6], [], 'None'),
    'Subethasmtp': ([1], [], 'None')
}

projDict = {
    'AaltoXml': ([1], [], 'None'),
}

def checkResults():
    for pid in projDict:
        bidList = projDict[pid][0]
        deprecatedBidList = projDict[pid][1]
        bidList = [bid for bid in bidList if bid not in deprecatedBidList]

        for bid in bidList:
            bidResultDir = 'results/{}/{}'.format(pid, bid)
            if not os.path.isdir(bidResultDir):
                print('[ERROR] results/{}/{} does not exist'.format(pid, bid))
            else:
                ochiaiFile = 'results/{}/{}/ochiai.ranking.csv'.format(pid, bid)
                # if the file does not exist or the file is empty or it only contains one line
                if not os.path.isfile(ochiaiFile):
                    print('[ERROR] results/{}/{}/ochiai.ranking.csv does not exist'.format(pid, bid))
                else:
                    linesNum = sp.check_output('cat results/{}/{}/ochiai.ranking.csv | wc -l '.format(pid, bid), shell=True, universal_newlines=True).strip()
                    if linesNum == '1' or linesNum == '0':
                        print('[ERROR] results/{}/{}/ochiai.ranking.csv is empty or only has one line!'.format(pid, bid))      

def main():
    os.makedirs(logDir, exist_ok=True)
    for pid in projDict:
        bidList = projDict[pid][0]
        deprecatedBidList = projDict[pid][1]
        bidList = [bid for bid in bidList if bid not in deprecatedBidList]
        sid = projDict[pid][2]
        if sid == 'None':
            sid = ""

        for bid in bidList:
            bidResultDir = 'results/{}/{}'.format(pid, bid)
            if os.path.isdir(bidResultDir):
                ochiaiFile = 'results/{}/{}/ochiai.ranking.csv'.format(pid, bid)
                linesNum = sp.check_output('cat results/{}/{}/ochiai.ranking.csv | wc -l '.format(pid, bid), shell=True, universal_newlines=True).strip()
                if not os.path.isfile(ochiaiFile) or (os.path.isfile(ochiaiFile) and linesNum == '1'):
                    print('Removing {} because the result is invalid'.format(bidResultDir))
                    shutil.rmtree(bidResultDir)
                else:
                    print("results/{}/{} already exists, skipping".format(pid, bid))
                    continue
            if os.path.isfile(os.path.join(logDir, pid + '-' + str(bid)+'.log')):
                os.remove(os.path.join(logDir, pid + '-' + str(bid)+'.log'))
            runGz(pid, str(bid), sid)

    waitPatchPoolFinish()

if __name__ == '__main__':
    main()
    # checkResults()
    
    # bugList = []
    # with Path('../bug_list.txt').open() as f:
    #     for line in f:
    #         line = line.strip()
    #         projName, bugId = line.split('_')
    #         projName = getD4jProjNameFromSimpleName(projName)
    #         bugId = str(int(bugId))
    #         bugList.append('{}_{}'.format(projName, bugId))
    # removedBugList = []
    # for proj in projDict:
    #     for bugId in projDict[proj][0]:
    #         bugId = str(bugId)
    #         if '{}_{}'.format(proj, bugId) not in bugList:
    #             removedBugList.append((proj, bugId))
    # for proj, bid in removedBugList:
    #     projDict[proj][0].remove(int(bid))
    # print(projDict)

    # main()
    # checkResults()