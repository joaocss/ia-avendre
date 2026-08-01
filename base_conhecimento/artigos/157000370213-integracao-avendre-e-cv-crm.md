---
id: 157000370213
titulo: "Integração Avendre e CV CRM"
categoria: "Avendre | Vitrine"
produto: vitrine
pasta: "Incorporadoras"
url: https://ajuda.avendre.com.br/support/solutions/articles/157000370213-integrac%C3%A3o-avendre-e-cv-crm
imagens: ["https://assets.cvcrm.com.br/kb/data/medias/446968/F13B569AE4A36A44F39267F5BA0E6BFC.png", "https://assets.cvcrm.com.br/kb/data/medias/446968/EA6E3068AFF45B0AD948F4AB163C5D9B.png", "https://assets.cvcrm.com.br/kb/data/medias/446968/735A75F2C8A8C8C38316A0DF7524E8B8.png", "https://assets.cvcrm.com.br/kb/data/medias/446968/360EF90EA2AC82445B850026F704F462.gif", "https://assets.cvcrm.com.br/kb/data/medias/446968/0CC2CDC1CE3C9DD589386FB8907F23A8.png", "https://assets.cvcrm.com.br/kb/data/medias/446968/57735A53B70270326AD9041BFA6373C1.png", "https://assets.cvcrm.com.br/kb/data/medias/446968/C8F7FE22855352496C731239AEBB4DE2.png", "https://assets.cvcrm.com.br/kb/data/medias/446968/DCF715DDF32D15A39455F55112694CA7.png", "https://assets.cvcrm.com.br/kb/data/medias/446968/6DEDB0947371254EF8A67381B13F0103.png", "https://assets.cvcrm.com.br/kb/data/medias/446968/7BFA62573F1A79A9DFC46A1B85376DCC.png", "https://assets.cvcrm.com.br/kb/data/medias/446968/D34F4FF1DD5FAAD910A19A4210B21035.png", "https://assets.cvcrm.com.br/kb/data/medias/446968/E69A90A6DD305C0B437A313309CFC8E6.png", "https://assets.cvcrm.com.br/kb/data/medias/446968/6CB9FA676DC93E594D5F2C4F41153A5B.png"]
videos: ["https://www.youtube.com/embed/9OhuYE2LtII?&wmode=opaque"]
---

# Integração Avendre e CV CRM

[](<https://s3.amazonaws.com/movidesk-files/BC5AA2CAB7FE63CE7BCC2BDB2786F6A0> "cv-weni.png")![](https://assets.cvcrm.com.br/kb/data/medias/446968/F13B569AE4A36A44F39267F5BA0E6BFC.png)

A Avendre é uma ferramenta multi-plataforma que coloca o corretor de imóveis no epicentro do negócio. Funcionando como uma vitrine abrangente para produtos dos incorporadores. Ele oferece acesso a uma variedade de opções para todos os corretores cadastrados em sua rede em todo o Brasil. Isso não apenas amplia a audiência dos corretores, mas também cria oportunidades substanciais tanto para esses profissionais quanto para as incorporadoras.  
  


No cenário brasileiro, onde o mercado imobiliário figura entre os maiores do mundo, movimentando bilhões de reais anualmente, o potencial disruptivo do Avendre é notável. Ao simplificar o acesso de corretores a uma gama diversificada de produtos imobiliários, o Avendre emerge como uma ferramenta capaz de revolucionar ainda mais esse setor. Sua proposta visa facilitar a busca ágil e eficaz dos melhores produtos para os clientes, proporcionando uma experiência mais eficiente aos corretores.  
  


Vale ressaltar que o Avendre se destaca como a única ferramenta em seu segmento que oferece integração nativa e suporte exclusivo do CVCRM. Tornando-se, assim, não apenas uma ferramenta profissional, mas uma aliada indispensável para os corretores e uma parceira estratégica para as incorporadoras.

* * *

## **Confira neste artigo:**

  * Pré-requisitos
  * Permissões do Perfil de Acesso
  * O que vai trafegar entre os sistemas?
  * Configurando a integração com o Avendre no CV
  * Selecionando o empreendimento e unidades



* * *

## **Pré-requisitos**

  * Ter o Token e ID da Incorporadora (gerados no Avendre);
  * Solicitar ao Suporte do CV a liberação da integração do Avendre no CV;
  * Habilitar permissões do Perfil de Acesso do CV.



  


## **Permissões do Perfil de Acesso**

A tela de configuração da integração com o Avendre é subdividida em quatro partes, e algumas dessas seções requerem permissões de perfil específicas para realizar modificações. A seguir, detalharemos o funcionamento dessas permissões:

Nas configurações de perfil de acesso, temos duas novas permissões de perfil que precisam ser habilitadas. 

Essas permissões podem ser encontradas na aba de **"Configurações" > "Integrações"**.

![](https://assets.cvcrm.com.br/kb/data/medias/446968/EA6E3068AFF45B0AD948F4AB163C5D9B.png)

  


  * **PERMISSÃO: MODIFICAR CONFIGURAÇÕES DA INCORPORADORA**

O perfil de acesso que possuir essa permissão terá a capacidade de modificar todas as informações relacionadas às seções **Parte 1: Configurações do usuário** e **Parte 2: Configurações da incorporadora.** Em outras palavras, o perfil com essa permissão poderá alterar o ID da incorporadora, cadastrar e modificar o TOKEN da incorporadora, modificar o Job de sincronização automática dos empreendimentos e atualizar o endereço e CNPJ da incorporadora, bem como os dados do responsável pela incorporadora.

  * **PERMISSÃO: SINCRONIZAR EMPREENDIMENTOS E UNIDADES**

O perfil de acesso que contar com essa permissão terá a capacidade de selecionar (inserir)e alterar os empreendimentos e unidades listados para sincronização com o Avendre. Além disso, poderá selecionar ou modificar a tabela de preços a ser enviada, ajustar as imagens ou vídeos do empreendimento a serem enviados, e alterar o gestor de parcerias do empreendimento.




**  
**

## **O que vai trafegar entre os sistemas?**

Vai ser trafegado entre as duas ferramentas os seguintes dados:

  * Informações do Empreendimento;
  * As informações da unidade;
  * As informações do Gestor de parcerias selecionado;
  * As imagens do empreendimento;
  * A tabela de preço selecionada no empreendimento;
  * As informações da incorporadora;
  * O token da incorporadora no Avendre;
  * O id da incorporadora no Avendre.


    
    
    Obs.: é uma premissa da integração criar a incorporadora primeiro no Avendre para que se tenha o token e ID da incorporadora.

  
![](https://assets.cvcrm.com.br/kb/data/medias/446968/735A75F2C8A8C8C38316A0DF7524E8B8.png)  
  


## **Configurando a integração com o Avendre no CV**

No CV, pesquise por**"Integrações"**.  
![](https://assets.cvcrm.com.br/kb/data/medias/446968/360EF90EA2AC82445B850026F704F462.gif)  
  
  
Busque por **"Avendre"** e clique em **"Configurar"**.  
![](https://assets.cvcrm.com.br/kb/data/medias/446968/0CC2CDC1CE3C9DD589386FB8907F23A8.png)  
  
  


A tela de configuração da integração com o Avendre é dividida em quatro partes. Mas, através desse vídeo você pode compreender melhor como funciona a integração:

  
  


**\- Parte 1: Configurações do usuário**

Na seção referente às configurações do usuário, é necessário inserir os dados da incorporadora do Avendre. É preciso informar o ID e o Token específico da incorporadora no Avendre para garantir a validação adequada dos dados.  
  


**\- Parte 2: Configurações da incorporadora**

Na seção dedicada às configurações da incorporadora, uma vez que o ID e o Token da incorporadora foram devidamente configurados (Parte 1) e validados, o Avendre enviará as informações da incorporadora para o CV, permitindo que o CV as salve.

  


Nessa seção, também é possível atualizar as informações da incorporadora se for necessário.

  

    
    
    Obs.: é importante destacar a existência de um conjunto de permissões de perfil, que vai ser detalhado mais a frente, as quais determinam se um usuário pode atualizar ou não as informações da incorporadora.

  


**\- Parte 3: Configurações gerais do empreendimento**

Na seção destinada às configurações gerais do empreendimento, o usuário terá a flexibilidade de realizar algumas ações. Isso inclui a capacidade de enviar manualmente informações para o Avendre por meio do botão "ENVIAR DADOS PARA SINCRONIZAÇÃO". Além disso, o usuário pode optar por configurar a sincronização automática com o Avendre através de um Job, bastando selecionar a opção "SIM". Nesse caso, a sincronização ocorrerá automaticamente a cada 24 horas. Também é possível acessar a tela de monitoramento para acompanhar o processo de sincronização.

  

    
    
    Obs.: a capacidade de ativar ou desativar o Job de sincronização está sujeita à permissão de perfil do usuário.

  


**\- Parte 4: Empreendimentos**

Na seção de empreendimentos, o usuário tem a opção de escolher quais empreendimentos e unidades deseja selecionar para sincronização com o Avendre.  
  

    
    
    Obs.: se não houver alterações nos empreendimentos e unidades previamente selecionados para envio, nenhuma requisição será enviada para o Avendre.

  


![](https://assets.cvcrm.com.br/kb/data/medias/446968/57735A53B70270326AD9041BFA6373C1.png)

  


  


## **Selecionando o empreendimento e unidades**

Na seção de **Empreendimentos** (Parte 4) da tela de integração é possível selecionar o empreendimento e a unidade como foi citado anteriormente.

Abaixo será detalhado melhor como fazer a seleção e quais informações enviar.  
**  
**

Na parte 4 da tela de configurações da integração, serão exibidos apenas os empreendimentos que possuem unidades disponíveis, ou seja, somente aquelas que estão com a situação**“Disponível”** podem ser exibidas e enviadas.  
  


Dentro da seção quatro, é possível localizar o empreendimento desejado por meio da pesquisa utilizando o ID do empreendimento, o nome do empreendimento e se foi sincronizado ou não.  
![](https://assets.cvcrm.com.br/kb/data/medias/446968/C8F7FE22855352496C731239AEBB4DE2.png)  


  


  


Ao localizar o empreendimento desejado, é necessário escolher as unidades que você deseja enviar. Para isso, clique nos três pontos localizados no lado direito da tela. Uma vez abertas as opções, selecione **"Unidades"**.

![](https://assets.cvcrm.com.br/kb/data/medias/446968/DCF715DDF32D15A39455F55112694CA7.png)

  


  


Ao selecionar **"Unidades"** , você será direcionado para a tela de escolha de unidades, onde o funcionamento dos filtros assemelha-se bastante à tela anterior. É possível filtrar as unidades com base no ID, nome, bloco e valor da unidade.

  

    
    
    Obs.: se alguma informação da unidade precisar de ajuste, é possível clicar em "Editar" e ser direcionado para a edição da unidade.

  


![](https://assets.cvcrm.com.br/kb/data/medias/446968/6DEDB0947371254EF8A67381B13F0103.png)

  


  


Nessa tela, temos 3 abas: **Unidades, Tabela de Preço** e **Configurações**.

![](https://assets.cvcrm.com.br/kb/data/medias/446968/7BFA62573F1A79A9DFC46A1B85376DCC.png)

  


  


**Aba de Unidades**

Na aba **"Unidades"** , é possível escolher as unidades que se deseja sincronizar com o Avendre. Pode-se optar por selecionar uma unidade específica ou todas, sendo que a seleção ocorre em blocos de 10 unidades por vez.

Após a seleção, surgirá o botão **"Enviar selecionados"** e todas as unidades escolhidas serão transferidas para o lado direito da tela.

Para remover unidades da seleção, após escolher as unidades desejadas, basta clicar no botão **"Remover selecionadas"****.** Todas as unidades selecionadas serão então movidas de volta para o lado esquerdo da tela.  
![](https://assets.cvcrm.com.br/kb/data/medias/446968/D34F4FF1DD5FAAD910A19A4210B21035.png)  
  
  


**Aba Tabela de preço**

Na aba **"Tabela de Preço"** , é possível escolher a tabela que alimentará os valores do lado do Avendre.  
  

    
    
    Obs.: serão exibidas apenas as tabelas de preço que estiverem aprovadas, sendo permitida a seleção de apenas uma tabela por empreendimento.

  


![](https://assets.cvcrm.com.br/kb/data/medias/446968/E69A90A6DD305C0B437A313309CFC8E6.png)

  


  


**Aba Configurações**

Na seção de configurações, o usuário pode escolher as imagens a serem enviadas, inclusive definindo a imagem decapa, incorporando vídeos e selecionando Coordenador de Parcerias específico para o empreendimento em questão.  
Após a seleção, basta clicar em **"Sincronizar mídias"** para efetuar o processo.

![](https://assets.cvcrm.com.br/kb/data/medias/446968/6CB9FA676DC93E594D5F2C4F41153A5B.png)

  


BOAS VENDAS!
