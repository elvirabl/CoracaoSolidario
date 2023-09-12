const Usuario = require('./usuario');
const Receptor = require('./receptor');

test('deve criar um receptor com os dados corretos', () => {
  const receptor = new Receptor('Giovana', 'giovanabruno@email.com', 'Sorocaba', 'Curativo A');
  expect(receptor.getNome()).toBe('Giovana');
  expect(receptor.getContato()).toBe('giovanabruno@email.com');
  expect(receptor.getTipo()).toBe('Receptor');
  expect(receptor.getRegiao()).toBe('Sorocaba');
  expect(receptor.getTipoCurativo()).toBe('Curativo A');
});
