class Usuario {
    constructor(nome, contato, tipo, regiao, tipoCurativo) {
      this.nome = nome;
      this.contato = contato;
      this.tipo = tipo;
      this.regiao = regiao;
      this.tipoCurativo = tipoCurativo;
    }
  
    getNome() {
      return this.nome;
    }
  
    setNome(novoNome) {
      this.nome = novoNome;
    }
  
    getContato() {
      return this.contato;
    }
  
    setContato(novoContato) {
      this.contato = novoContato;
    }
  
    getTipo() {
      return this.tipo;
    }
  
    setTipo(novoTipo) {
      this.tipo = novoTipo;
    }
  
    getRegiao() {
      return this.regiao;
    }
  
    setRegiao(novaRegiao) {
      this.regiao = novaRegiao;
    }
  
    getTipoCurativo() {
      return this.tipoCurativo;
    }
  
    setTipoCurativo(novoTipoCurativo) {
      this.tipoCurativo = novoTipoCurativo;
    }
  }
  
  module.exports = Usuario;
  