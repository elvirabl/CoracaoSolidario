const Usuario = require('./usuario');

describe('Classe Usuario', () => {
  test('deve criar um usuário com os dados corretos', () => {
    const usuario = new Usuario('Giovana', 'giovanabruno@email.com', 'Receptor', 'Sorocaba', 'Curativo A');
    expect(usuario.getNome()).toBe('Giovana');
    expect(usuario.getContato()).toBe('giovanabruno@email.com');
    expect(usuario.getTipo()).toBe('Receptor');
    expect(usuario.getRegiao()).toBe('Sorocaba');
    expect(usuario.getTipoCurativo()).toBe('Curativo A');
  });

  test('setNome deve atualizar o nome corretamente', () => {
    const usuario = new Usuario('Giovana', 'giovanabruno@email.com', 'Receptor', 'Sorocaba', 'Curativo A');
    usuario.setNome('Henriqueta');
    expect(usuario.getNome()).toBe('Henriqueta');
  });

  test('setContato deve atualizar o contato corretamente', () => {
    const usuario = new Usuario('Giovana', 'giovanabruno@email.com', 'Receptor', 'Sorocaba', 'Curativo A');
    usuario.setContato('henriqueta@email.com');
    expect(usuario.getContato()).toBe('henriqueta@email.com');
  });

  test('setTipo deve atualizar o tipo corretamente', () => {
    const usuario = new Usuario('Giovana', 'giovanabruno@email.com', 'Receptor', 'Sorocaba', 'Curativo A');
    usuario.setTipo('Doador');
    expect(usuario.getTipo()).toBe('Doador');
  });

  test('setRegiao deve atualizar a região corretamente', () => {
    const usuario = new Usuario('Giovana', 'giovanabruno@email.com', 'Receptor', 'Sorocaba', 'Curativo A');
    usuario.setRegiao('Sorocaba-Zona Oeste');
    expect(usuario.getRegiao()).toBe('Sorocaba-Zona Oeste');
  });

  test('setTipoCurativo deve atualizar o tipoCurativo corretamente', () => {
    const usuario = new Usuario('Giovana', 'giovanabruno@email.com', 'Receptor', 'Sorocaba', 'Curativo A');
    usuario.setTipoCurativo('Micropore Anti Alérgico');
    expect(usuario.getTipoCurativo()).toBe('Micropore Anti Alérgico');
  });
});
