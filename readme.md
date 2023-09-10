Coração Solidário - Uma melhor qualidade de vida as GUERREIRAS !!! Contra o câncer de mama.

![Alt text](../coracao.png)

A inspiração veio da minha melhor amiga Greice Giacomelli, que é uma profissional excepcional, tanto na programação como na radiologia, ela viveu momentos acompanhado pacientes com câncer de mama, e após alguns relatos, percebeu que as pacientes não tinham melhoras significativa pelo motivo de não conseguir um curativo novo e limpo para suas feridas, muitas vezes pós cirúrgica. Na On19, ela escreveu esse código com maestria, e desde então, essa premissa não me sai da cabeça. Gostaria muito de escrever o Coração Solidário novamente, aproveitando todo o aprendizado dessa nova etapa do curso da { Reprograma}

O Coração Solidário atende mulheres de baixa renda, com câncer de mama, pós cirurgica, pegam o transporte público, muitas vezes, lotado, pra tentar conseguir um curativo expecífico no SUS. Muitas vezes não tem o curativo necessário, elas ficam com o curativo velho, e simplesmente assim, lutando, elas voltam no dia seguinte, correndo grande risco de infecção.

Uma solução para esse problema é criar um banco de dados, onde permita conectar recepitores e doadores de curativos, que infelizmente sobra quando se perde a guerra contra o câncer, onde doadores e receptores estão localizados na mesma região, economizando tempo e exposição a possíveis infecções.

Cadastro de receptor e doador, herdando dados de uma classe cadastro único. Pensando em que um receptor pode se tornar um doador e vice e versa.
controle com sistema PEPS de receptores aos curativos disponíveis, autenticação por senha(gerada pelo ambulatório médico)

Para o futuro, monetizar vendendo espaço para empresas parceiras como farmácias, consultórios, clínicas, industria farmacêutica.
## Tecnologias utilizadas  
• Node.js  
• Jest  
• Git  
## Pacotes utilizados para conecxão com a API 
• express  
• nodemon  
• dotenv-safe  
• mongoose  
• cors  
• save  

# Instruções de instalação  
## Clonar o repositório
$ git clone https://github.com/elvirabl/CoracaoSolidario
## Instalar as dependências  
$ npm install  
## Executar o servidor  
$ npm start  
## Getter´s e Setter´s  
GET - https://buscandosonhos.onrender.com/buscandosonhos/ancestor/all  
GET - https://buscandosonhos.onrender.com/buscandosonhos/ancestor/ID  
GET - https://buscandosonhos.onrender.com/buscandosonhos/members/all  
GET - https://buscandosonhos.onrender.com/buscandosonhos/members/ID  
POST - https://buscandosonhos.onrender.com/buscandosonhos/ancestor/add/  
POST - https://buscandosonhos.onrender.com/buscandosonhos/members/add  
PATCH - https://buscandosonhos.onrender.com/buscandosonhos/members/ID  
PATCH - https://buscandosonhos.onrender.com/buscandosonhos/ancestor/ID  
DELETE - https://buscandosonhos.onrender.com/buscandosonhos/members/ID   
 
## Gostaria de contribuir?  
1. Fork o projeto;  
2. Crie uma branch para realizar suas alterações: git checkout -b feature/nome-da-sua-branch  
3. Commit suas alterações e abra um pull request  

## Agradecimentos
Agradeço a todas as profissionais da equipe Reprograma, em especial a Sra. Raquel, facilitadora, a Sra. Camila, professora, a Sra. Louse Costa, que me inspirou a continuar.  
Gratidão a minha grande amiga Graice Pereira Giacomelli, que me auxiliou em cada momento difícil.  
Gratidão a minha família (humana e pet), que nunca me abandonou.  
Gratidão a Grande Deusa que me guiou nessa grande aventura no mundo da programação.  


## MAPA

coracaoSolidario/
  └── src/
      ├── Usuario.js
      |── Doador.js
      |── Receptor.js
      |── Server.js
         └── Index.js/

Usuario: Uma classe base que contém informações comuns a todos os usuários (nome, contato, tipo(doador ou receptor), região(mostra onde está o doador que tem o tipo de curativo igual solicitado pelo Receptor , tipo de curativo (string), id). Doador: Uma subclasse de Usuariométodos e propriedades específicas para doadores.(solicita tipo de decorativo e se liga ao receptor por tipo igual de utilitário e igual região, o doador pode se tornar Receptor) Receptor: Uma subclasse de Usuariométodos e propriedades específicas para doadores.( se liga ao receptor por tipo igual de curativo e igual região, o Receptor pode se tornar Doador) Organizado no sistema SRC (modelos, controlador e rotas)