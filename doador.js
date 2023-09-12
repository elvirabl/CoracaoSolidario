const Usuario = require('./usuario');

class Doador extends Usuario {
  constructor(nome, contato, regiao, tipoCurativo) {
    super(nome, contato, 'Doador', regiao, tipoCurativo);
  }

  doar(curativo, receptor) {
    console.log(`${this.nome} doou um curativo ${curativo.tipo} para ${receptor.nome}`);
  }
}

module.exports = Doador;
