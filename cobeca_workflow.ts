import { workflow, node, trigger } from '@n8n/workflow-sdk';

const startTrigger = trigger({
  type: 'n8n-nodes-base.executeWorkflowTrigger',
  version: 1.1,
  config: { 
    name: 'Recibir Pedido',
    parameters: {
      inputSource: 'workflowInputs',
      workflowInputs: {
        values: [
          { name: 'items', type: 'string' },
          { name: 'cod_cliente', type: 'string' },
          { name: 'cod_cliente_len', type: 'number' },
          { name: 'carpeta_pedidos', type: 'string' }
        ]
      }
    },
    position: [100, 300] 
  },
  output: [{ items: [] }]
});

const obtenerCorrelativo = node({
  type: 'n8n-nodes-base.microsoftSql',
  version: 1.1,
  config: {
    name: 'Obtener Correlativo',
    parameters: {
      operation: 'executeQuery',
      query: "=UPDATE Proveedores.Pedidos_FTP_Secuencia SET UltimoCorrelativo = UltimoCorrelativo + 1, UpdatedAt = SYSDATETIME() WHERE DrogueriaCode = 'COBECA13'; SELECT UltimoCorrelativo AS correlativo FROM Proveedores.Pedidos_FTP_Secuencia WHERE DrogueriaCode = 'COBECA13';"
    },
    position: [300, 300]
  },
  output: [{ correlativo: 1 }]
});

const generarTxt = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Generar Archivo TXT',
    parameters: {
      mode: 'runOnceForAllItems',
      language: 'javaScript',
      jsCode: `
const triggerData = $('Recibir Pedido').first().json;
const corrData = $('Obtener Correlativo').first().json;

const items = triggerData.items || [];
const codCliente = triggerData.cod_cliente || '0';
const carpeta = triggerData.carpeta_pedidos || '/';
const correlativo = corrData.correlativo || 1;

// Cobeca format
const fileName = 'cobeca_pedido_' + correlativo + '.txt';

const lines = items.map(item => {
  return \`\${item.codigo_producto};\${item.cantidad}\`;
});
const fileContent = lines.join('\\n');

return [{
  json: {
    fileName,
    fileContent,
    fullPath: \`\${carpeta}\${fileName}\`,
    correlativo,
    drogueria_code: 'COBECA13'
  }
}];
      `
    },
    position: [500, 300]
  },
  output: [{ fileName: 'test.txt' }]
});

const subirFtp = node({
  type: 'n8n-nodes-base.ftp',
  version: 1,
  config: {
    name: 'Subir Pedido FTP',
    parameters: {
      protocol: 'ftp',
      operation: 'upload',
      path: '={{ $json.fullPath }}',
      binaryData: false,
      fileContent: '={{ $json.fileContent }}'
    },
    position: [700, 300]
  },
  output: [{}]
});

export default workflow('sub-workflow-generar-txt-cobeca', '[SUB] [Pedidos] - Generar TXT Cobeca y Subir FTP')
  .add(startTrigger)
  .to(obtenerCorrelativo
    .to(generarTxt
      .to(subirFtp)
    )
  );
