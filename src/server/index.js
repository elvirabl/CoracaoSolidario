const Receptor = require('../receptor');
const Doador = require('../doador');
const Curativo = require('../curativo');
const Usuario = require("../usuario")

const receptor1 = new Receptor('Jane', 'tiajane@gmail.com', 'Zona Oeste', 'Curativo z');
const receptor2 = new Receptor('Elvira', 'elvirabrunoleme@gmail.com', 'Zona Norte', 'Curativo Y');
const doador1 = new Doador('AnaLú', 'minhalinda@gmail.com', 'Zona Norte', 'Curativo X');
const doador2 = new Doador('Eurofarma', 'contatodoacao@eurofarma.com.br', 'Zona Norte', 'Curativo Y');
const curativoX = new Curativo('Curativo X');
const curativoY = new Curativo('Curativo Y');

receptor1.solicitarDoacao(curativoX, [doador1, doador2]);
receptor2.solicitarDoacao(curativoY, [doador1, doador2]);
// Crie um novo objeto Usuario
const usuario = new Usuario('Diva', 'donadiva@email.com', 'Receptor', 'Zona Sul', 'Curativo A');

// Use os getters para acessar propriedades
console.log('Nome:', usuario.getNome()); // Saída: Nome: João
console.log('Contato:', usuario.getContato()); // Saída: Contato: joao@email.com
console.log('Tipo:', usuario.getTipo()); // Saída: Tipo: Receptor
console.log('Região:', usuario.getRegiao()); // Saída: Região: São Paulo
console.log('Tipo de Curativo:', usuario.getTipoCurativo()); // Saída: Tipo de Curativo: Curativo A

// Use os setters para modificar propriedades
usuario.setNome('Tia Danuzia');
console.log('Novo:', usuario.getNome()); // Saída: Novo Nome: Maria
usuario.setContato('danuzia@email.com');
console.log('Novo Contato:', usuario.getContato()); // Saída: Novo Contato: maria@email.com

usuario.setTipo('Doador');
console.log('Novo Tipo:', usuario.getTipo()); // Saída: Novo Tipo: Doador

usuario.setRegiao('Zona Leste');
console.log('Nova Região:', usuario.getRegiao()); // Saída: Nova Região: Rio de Janeiro

usuario.setTipoCurativo('Curativo B');
console.log('Novo Tipo de Curativo:', usuario.getTipoCurativo()); // Saída: Novo Tipo de Curativo: Curativo B
