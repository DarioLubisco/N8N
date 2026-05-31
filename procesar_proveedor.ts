import { workflow, node, trigger, switchCase } from '@n8n/workflow-sdk';

const startTrigger = trigger({
  type: 'n8n-nodes-base.executeWorkflowTrigger',
  version: 1.1,
  config: { 
    name: 'Recibir Proveedor',
    parameters: {
      inputSource: 'workflowInputs',
      workflowInputs: {
        values: [{ name: 'nombre', type: 'string' }]
      }
    },
    position: [100, 400] 
  },
  output: [{ nombre: 'Gama' }]
});

const switchNode = switchCase({
  version: 3.2,
  config: {
    name: 'Ruta por Proveedor',
    parameters: {
      dataType: 'string',
      value: '={{ $json.nombre }}',
      rules: {
        rules: [
          { value: 'Gama', output: 0 },
          { value: 'NENA', output: 1 },
          { value: 'Biogenetica', output: 2 },
          { value: 'DROCERCA', output: 3 }
        ]
      },
      fallbackOutput: 4
    },
    position: [350, 400]
  }
});

const etlGama = node({
  type: 'n8n-nodes-base.ssh',
  version: 1,
  config: {
    name: 'ETL Gama',
    parameters: {
      command: 'curl -s -u GAMA@electrodomotica.com.ve:SK1OiDJaTKtT ftp://ftp.electrodomotica.com.ve/Inventario/INVENTARIO.Txt | python3 /opt/scripts/droguerias/gama.py'
    },
    position: [650, 50]
  },
  output: [{ exitCode: 0 }]
});

const etlNena = node({
  type: 'n8n-nodes-base.ssh',
  version: 1,
  config: {
    name: 'ETL Nena',
    parameters: {
      command: 'curl -s -u c344-foraneo:c2wi6yl1 ftp://ftp.dronena.com/Maracay/C344/Inventario.txt | python3 /opt/scripts/droguerias/nena.py'
    },
    position: [650, 200]
  },
  output: [{ exitCode: 0 }]
});

const downloadBiogenetica = node({
  type: 'n8n-nodes-base.ftp',
  version: 1,
  config: {
    name: 'Download Biogenetica',
    parameters: {
      operation: 'download',
      path: '/inventario/inventario.txt'
    },
    position: [650, 350]
  },
  output: [{}]
});

const uploadBiogenetica = node({
  type: 'n8n-nodes-base.ssh',
  version: 1,
  config: {
    name: 'Upload Biogenetica',
    parameters: {
      resource: 'file',
      operation: 'upload',
      path: '/tmp/',
      options: { fileName: 'biogenetica_raw.txt' }
    },
    position: [850, 350]
  },
  output: [{}]
});

const runBiogenetica = node({
  type: 'n8n-nodes-base.ssh',
  version: 1,
  config: {
    name: 'Run Biogenetica Script',
    parameters: {
      command: 'cat /tmp/biogenetica_raw.txt | python3 /opt/scripts/droguerias/biogenetica.py'
    },
    position: [1050, 350]
  },
  output: [{ exitCode: 0 }]
});

const etlDrocerca = node({
  type: 'n8n-nodes-base.ssh',
  version: 1,
  config: {
    name: 'ETL Drocerca',
    parameters: {
      command: 'curl -s -u C0005r:008376238 ftp://drocerca.proteoerp.org/inventario.txt | python3 /opt/scripts/droguerias/drocerca.py'
    },
    position: [650, 500]
  },
  output: [{ exitCode: 0 }]
});

const etlGenerico = node({
  type: 'n8n-nodes-base.ssh',
  version: 1,
  config: {
    name: 'ETL Generico',
    parameters: {
      command: '=echo "Proveedor genérico {{ $json.nombre }} sin configuración FTP específica"'
    },
    position: [650, 650]
  },
  output: [{ exitCode: 0 }]
});

export default workflow('sub-workflow-procesar-proveedor-v4', '[ETL] Sub-Workflow: Procesar Proveedor V4')
  .add(startTrigger)
  .to(switchNode
    .onCase(0, etlGama)
    .onCase(1, etlNena)
    .onCase(2, downloadBiogenetica.to(uploadBiogenetica.to(runBiogenetica)))
    .onCase(3, etlDrocerca)
    .onCase(4, etlGenerico)
  );
