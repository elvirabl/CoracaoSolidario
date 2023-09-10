const Usuario = require('./usuario');

class Receptor extends Usuario {
  constructor(nome, contato, regiao, tipoCurativo) {
    super(nome, contato, 'Receptor', regiao, tipoCurativo);
  }

  solicitarDoacao(curativo, doadores) {
    const doadorDisponivel = doadores.find(doador => doador.tipoCurativo === curativo.tipo && doador.regiao === this.regiao);
    if (doadorDisponivel) {
      doadorDisponivel.doar(curativo, this);
    } else {
      console.log(`Não há doadores disponíveis para ${curativo.tipo} na região ${this.regiao}`);
    }
  }
}

module.exports = Receptor;
