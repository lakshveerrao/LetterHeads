// ================= the Atlas: the real Earth, following the history clock =================
// Imagery: NASA Blue Marble Next Generation with topography and bathymetry (5400 x 2700).
// Shelves and ice: NOAA ETOPO1 at 10 arc-minutes, sea level from the curve below, ice outlines hand-traced at the last glacial maximum.
const AU=15,AMW=360*AU,AMH=180*AU,ALAT0=84,ALAT1=-62;
const ax=lon=>(lon+180)*AU,ay=lat=>(90-lat)*AU;
// global sea level, metres relative to today (approximate; after Spratt and Lisiecki 2016, and Lambeck and colleagues 2014)
const SEA=[[300000,-30],[280000,-70],[250000,-100],[240000,-15],[230000,-60],[215000,-20],[200000,-50],[175000,-80],[150000,-110],[140000,-125],[130000,-20],[125000,5],[118000,-10],[110000,-40],[100000,-30],[90000,-50],[80000,-30],[70000,-70],[62000,-85],[55000,-65],[45000,-70],[35000,-75],[30000,-85],[26000,-120],[21000,-130],[19000,-125],[16000,-105],[14500,-85],[12500,-65],[11500,-55],[10000,-40],[9000,-28],[8000,-15],[7000,-5],[6000,-2],[4000,0],[0,0]];
function seaLevel(y){y=clamp(y,0,300000);for(let i=1;i<SEA.length;i++)if(y>=SEA[i][0]){const[y0,s0]=SEA[i-1],[y1,s1]=SEA[i];return lerp(s1,s0,(y-y1)/(y0-y1));}return 0;}
const iceFrac=y=>clamp((-seaLevel(y)-10)/115,0,1);
function yearLabel(y){if(y<1)return"today";const r=y>=10000?Math.round(y/1000)*1000:y>=1000?Math.round(y/100)*100:Math.round(y/10)*10;return`${r.toLocaleString()} years ago`;}
const CHECKED=1,UNCHECKED=0;
// where Letterheads live, following humanity's documented routes (earliest widely accepted dates; debated ones say so)
const NODES=[
 {id:"irhoud",lon:-8.9,lat:31.9,y:300000,name:"the families of the Atlas Mountains",when:"About 300,000 years ago",text:"At Jebel Irhoud in Morocco lie the oldest known remains of our species.",src:["Hublin and colleagues, 2017, Nature","https://www.eva.mpg.de/press/news/2017/2017-06-07-the-first-of-our-kind",CHECKED]},
 {id:"rift",lon:36.1,lat:4.2,y:300000,from:"irhoud",name:"the families of the Rift Valley",when:"By about 233,000 years ago at Omo Kibish",text:"East Africa's lakes and rivers are home to some of the earliest people.",src:["Vidal and colleagues, 2022, Nature","https://doi.org/10.1038/s41586-021-04275-8",CHECKED]},
 {id:"florisbad",lon:26.1,lat:-28.8,y:259000,from:"rift",name:"the families of the southern grasslands",when:"About 260,000 years ago at Florisbad",text:"People live across Africa, from north to south.",src:["Grün and colleagues, 1996, Nature","https://doi.org/10.1038/382500a0",CHECKED]},
 {id:"levant",lon:35.2,lat:32.7,y:180000,from:"rift",name:"the families of the Levant",when:"About 194,000 to 177,000 years ago at Misliya",text:"Early ventures out of Africa reach the Levant. For a long time they do not spread further.",src:["Hershkovitz and colleagues, 2018, Science","https://doi.org/10.1126/science.aap8369",CHECKED]},
 {id:"arabia",lon:40.2,lat:28.1,y:85000,from:"levant",name:"the families of green Arabia",when:"About 85,000 years ago at Al Wusta",text:"In a wetter time, lakes dot the Arabian desert, and people follow them.",src:["Groucutt and colleagues, 2018, Nature Ecology and Evolution","https://doi.org/10.1038/s41559-018-0518-2",CHECKED]},
 {id:"sarabia",lon:48,lat:15.5,y:72000,from:"rift",name:"the families of the southern coasts",when:"About 70,000 to 60,000 years ago (debated)",text:"The main journey out of Africa begins, perhaps across the narrow strait at the mouth of the Red Sea.",src:["Fernandes and colleagues, 2012, American Journal of Human Genetics","https://pmc.ncbi.nlm.nih.gov/articles/PMC3276663",CHECKED]},
 {id:"india",lon:78,lat:21,y:68000,from:"sarabia",name:"the families of the Indian plains",when:"By 65,000 to 50,000 years ago (debated)",text:"People reach South Asia; exactly when is still argued over.",src:["Mellars and colleagues, 2013, PNAS","https://pmc.ncbi.nlm.nih.gov/articles/PMC3696785",CHECKED]},
 {id:"sunda",lon:108,lat:2,y:66000,from:"india",name:"the families of Sunda",when:"By about 65,000 to 50,000 years ago (debated)",text:"With the sea low, Borneo, Sumatra and Java are joined to Asia as one land called Sunda.",src:["Westaway and colleagues, 2017, Nature","https://doi.org/10.1038/nature23452",CHECKED]},
 {id:"sahul",lon:132.9,lat:-12.5,y:64000,from:"sunda",name:"the families of Sahul",when:"About 65,000 to 50,000 years ago (debated)",text:"People cross open sea to reach Sahul, the joined land of Australia and New Guinea. Madjedbebe holds some of the oldest evidence.",src:["Clarkson and colleagues, 2017, Nature","https://doi.org/10.1038/nature22968",CHECKED]},
 {id:"europe",lon:25.2,lat:42.9,y:47000,from:"levant",name:"the families of the Balkans",when:"About 47,000 to 43,000 years ago at Bacho Kiro",text:"People reach Europe, where Neanderthals already live, and mammoths roam the cold plains.",src:["Hublin and colleagues, 2020, Nature","https://doi.org/10.1038/s41586-020-2259-z",CHECKED]},
 {id:"westeu",lon:1.5,lat:45,y:42000,from:"europe",name:"the families of the western valleys",when:"By about 42,000 years ago",text:"Cave painters will soon decorate the valleys of what is now France and Spain.",src:["Wood and colleagues, 2014, Journal of Human Evolution","https://doi.org/10.1016/j.jhevol.2013.12.017",CHECKED]},
 {id:"siberiaW",lon:71.2,lat:57.7,y:45000,from:"levant",name:"the families of the Irtysh",when:"About 45,000 years ago at Ust'-Ishim",text:"Hunters live on the cold steppe of western Siberia.",src:["Fu and colleagues, 2014, Nature","https://doi.org/10.1038/nature13810",CHECKED]},
 {id:"eastasia",lon:115.9,lat:39.6,y:40000,from:"sunda",name:"the families of the northern plains of China",when:"About 40,000 years ago at Tianyuan",text:"People live in the hills near today's Beijing.",src:["Fu and colleagues, 2013, PNAS","https://doi.org/10.1073/pnas.1221359110",CHECKED]},
 {id:"japan",lon:137.5,lat:36,y:38000,from:"eastasia",name:"the families of the islands",when:"About 38,000 years ago",text:"People reach the islands of Japan.",src:["Gakuhari and colleagues, 2020, Communications Biology","https://pmc.ncbi.nlm.nih.gov/articles/PMC7447786",CHECKED]},
 {id:"yana",lon:135.4,lat:70.7,y:32000,from:"siberiaW",name:"the families of the Yana",when:"About 32,000 years ago",text:"Mammoth hunters live far above the Arctic Circle.",src:["Pitulko and colleagues, 2004, Science","https://doi.org/10.1126/science.1085219",CHECKED]},
 {id:"beringia",lon:-168,lat:64.5,y:25000,from:"yana",name:"the families of Beringia",when:"Perhaps 25,000 years ago (debated)",text:"With the sea low, Asia and America are one land. Genetic studies suggest people waited here for thousands of years.",src:["Tamm and colleagues, 2007, PLoS ONE","https://pmc.ncbi.nlm.nih.gov/articles/PMC1952074",CHECKED]},
 {id:"whitesands",lon:-106.3,lat:32.8,y:23000,from:"beringia",name:"the families of the southwest",when:"About 23,000 to 21,000 years ago (debated)",text:"Footprints at White Sands, New Mexico, may be the oldest sign of people in the Americas.",src:["Bennett and colleagues, 2021, Science","https://doi.org/10.1126/science.abg7586",CHECKED]},
 {id:"monteverde",lon:-73.2,lat:-41.5,y:14500,from:"whitesands",name:"the families of the far south",when:"About 14,500 years ago at Monte Verde (debated)",text:"People live near the southern tip of the Americas.",src:["Dillehay and colleagues, 2015, PLOS ONE","https://doi.org/10.1371/journal.pone.0141923",CHECKED]},
 {id:"amazon",lon:-54.5,lat:-2,y:13000,from:"whitesands",name:"the families of the great river",when:"By about 13,000 to 11,000 years ago",text:"People live along the Amazon.",src:["Roosevelt and colleagues, 1996, Science","https://ui.adsabs.harvard.edu/abs/1996Sci...272..373R/abstract",CHECKED]},
 {id:"greenland",lon:-51,lat:69,y:4500,from:"beringia",name:"the families of the ice coast",when:"About 4,500 years ago",text:"The first people reach Greenland from the Arctic of North America.",src:["National Museum and Archives of Greenland","https://en.nka.gl/museum/exhibitions/the-first-people",CHECKED]},
 {id:"lapita",lon:168.3,lat:-17.7,y:3000,from:"sahul",name:"the families of the far islands",when:"About 3,000 years ago",text:"Seafarers settle the islands of the southwest Pacific.",src:["Valentin and colleagues, 2016, PNAS","https://doi.org/10.1073/pnas.1516186113",CHECKED]},
 {id:"hawaii",lon:-155.5,lat:19.8,y:1000,from:"lapita",name:"the families of Hawaii",when:"About 1,000 to 800 years ago",text:"Voyagers find the islands of Hawaii across thousands of kilometres of ocean.",src:["Sear and colleagues, 2020, PNAS","https://doi.org/10.1073/pnas.1920975117",CHECKED]},
 {id:"aotearoa",lon:174.5,lat:-41,y:750,from:"lapita",name:"the families of Aotearoa",when:"About 750 years ago",text:"The last great land to be settled: Aotearoa, New Zealand.",src:["Wilmshurst and colleagues, 2011, PNAS","https://doi.org/10.1073/pnas.1015876108",CHECKED]}];
const NODE={};NODES.forEach(n=>{NODE[n.id]=n;n.x=ax(n.lon);n.yy=ay(n.lat);});
// real events, placed where and when they happened
const EVENTS=[
 {lon:98.8,lat:2.6,y:74000,name:"Toba erupts",text:"One of the largest volcanic eruptions of the last two million years, on Sumatra.",src:["NASA Earth Observatory","https://science.nasa.gov/earth/earth-observatory/toba-caldera-7380",CHECKED]},
 {lon:21.2,lat:-34.4,y:77000,name:"Engraved ochre at Blombos",text:"Someone scratches a crosshatched pattern into ochre: one of the oldest known designs.",src:["Henshilwood and colleagues, 2002, Science","https://doi.org/10.1126/science.1067575",CHECKED]},
 {lon:4.4,lat:44.4,y:36000,name:"Chauvet cave paintings",text:"Horses, lions and mammoths are painted deep in a cave.",src:["UNESCO World Heritage Centre, Grotte Chauvet-Pont d'Arc","https://whc.unesco.org/en/list/1426",CHECKED]},
 {lon:117.2,lat:28.7,y:20000,name:"The first pottery",text:"Cooking pots are made at Xianrendong cave, long before farming.",src:["Wu and colleagues, 2012, Science","https://doi.org/10.1126/science.1218643",CHECKED]},
 {lon:1.2,lat:45.05,y:22000,name:"Lascaux cave paintings",text:"Hundreds of animals are painted on the walls of Lascaux.",src:["French Ministry of Culture, Lascaux site","https://archeologie.culture.gouv.fr/lascaux/en/dating-figures-lascaux",CHECKED]},
 {lon:38.9,lat:37.2,y:11600,name:"Göbekli Tepe",text:"Great carved stone pillars are raised, before farming, pottery or writing.",src:["UNESCO World Heritage Centre, Göbekli Tepe","https://whc.unesco.org/en/list/1572",CHECKED]},
 {lon:41,lat:35.6,y:11500,name:"Farming begins",text:"In the Fertile Crescent, people begin to sow wheat and barley and keep animals.",src:["Zeder, 2011, Current Anthropology","https://doi.org/10.1086/659307",CHECKED]},
 {lon:-99.5,lat:18.3,y:9000,name:"Maize is tamed",text:"In Mexico's Balsas valley, a wild grass slowly becomes maize.",src:["Piperno and colleagues, 2009, PNAS","https://doi.org/10.1073/pnas.0812525106",CHECKED]},
 {lon:112,lat:30,y:9000,name:"Rice farming",text:"Along the Yangtze, people begin to grow rice (the timing is debated).",src:["Gross and Zhao, 2014, PNAS","https://doi.org/10.1073/pnas.1308942110",CHECKED]},
 {lon:32.8,lat:37.7,y:9100,name:"Çatalhöyük",text:"Thousands of people live together in a town of mud-brick houses.",src:["UNESCO World Heritage Centre, Neolithic Site of Çatalhöyük","https://whc.unesco.org/en/list/1405",CHECKED]},
 {lon:3,lat:54.6,y:8200,name:"Doggerland drowns",text:"The rising sea, and a great tsunami from the Storegga slide, drown most of the land between Britain and Europe.",src:["Walker and colleagues, 2020, Antiquity","https://doi.org/10.15184/aqy.2020.49",CHECKED]},
 {lon:12,lat:22,y:5500,name:"The Sahara dries",text:"The long wet period ends, and the green Sahara turns to desert.",src:["Shanahan and colleagues, 2015, Nature Geoscience","https://impacts.ucar.edu/en/publications/the-time-transgressive-termination-of-the-african-humid-period",CHECKED]},
 {lon:45.6,lat:31.3,y:5200,name:"Writing at Uruk",text:"Scribes press marks into clay: cuneiform, one of the first writing systems.",src:["Cuneiform Digital Library Initiative, Uruk IV tablet IM 133701","https://cdli.earth/artifacts/3300",CHECKED]},
 {lon:31.9,lat:26.2,y:5200,name:"Hieroglyphs",text:"In Egypt, writing with pictures and sounds begins.",src:["British Museum, Hieroglyphs timeline","https://www.britishmuseum.org/exhibitions/hieroglyphs-unlocking-ancient-egypt/egyptian-hieroglyphs-decipherment-timeline",CHECKED]},
 {lon:72.9,lat:30.6,y:4600,name:"Indus script",text:"The cities of the Indus valley use a script no one can read today.",src:["Parpola, Harappa.com","https://www.harappa.com/sites/default/files/pdf/indusscript(2).pdf",CHECKED]},
 {lon:32.4,lat:25.95,y:3850,name:"The first alphabet",text:"At Wadi el-Hol, pictures become sounds. The A is an ox's head, the B a house, the O an eye.",src:["Simons, 2011, Rosetta 9","https://rosetta.bham.ac.uk/wp-content/uploads/2024/02/Simons_Proto-Sinaitic_Rosetta9.pdf",CHECKED]},
 {lon:114.3,lat:36.1,y:3200,name:"Oracle bones",text:"At Anyang, questions to the ancestors are carved on bones: the ancestor of Chinese writing.",src:["UNESCO World Heritage Centre, Yin Xu","https://whc.unesco.org/en/list/1114/",CHECKED]},
 {lon:35.6,lat:34.1,y:3050,name:"The Phoenician alphabet",text:"Traders at Byblos spread a 22-letter alphabet across the sea.",src:["UNESCO World Heritage Centre, Byblos","https://whc.unesco.org/en/list/295/",CHECKED]},
 {lon:23.7,lat:38,y:2800,name:"The Greek alphabet",text:"The Greeks borrow the alphabet and add letters for vowels.",src:["Encyclopaedia Britannica, Greek language: the Greek alphabet","https://www.britannica.com/topic/Greek-language/The-Greek-alphabet",CHECKED]},
 {lon:12.5,lat:41.9,y:2779,name:"Rome",text:"By tradition, Rome is founded. Its letters become the ones you are reading.",src:["Cavendish, 2003, History Today","https://www.historytoday.com/archive/months-past/foundation-rome",CHECKED]},
 {lon:-89.3,lat:17.3,y:2300,name:"Maya writing",text:"At San Bartolo, the Maya paint some of their earliest glyphs.",src:["Saturno and colleagues, 2006, Science","https://doi.org/10.1126/science.1121745",CHECKED]},
 {lon:8.27,lat:50,y:576,name:"The printing press",text:"In Mainz, Gutenberg prints with movable metal letters.",src:["Library of Congress, The Gutenberg Bible","https://www.loc.gov/exhibits/bibles/the-gutenberg-bible.html",CHECKED]}];
EVENTS.forEach(e=>{e.x=ax(e.lon);e.yy=ay(e.lat);});
// names that matter only at certain times
const PLACES=[
 {lon:-170,lat:62,name:"Beringia",when:(y,sl)=>sl<-50},{lon:3,lat:55.3,name:"Doggerland",when:(y,sl)=>sl<-30},{lon:109,lat:4,name:"Sunda",when:(y,sl)=>sl<-45},
 {lon:138,lat:-9,name:"Sahul",when:(y,sl)=>sl<-45},{lon:-92,lat:59,name:"Laurentide ice sheet",when:(y,sl)=>iceFrac(y)>.35},{lon:23,lat:65,name:"Fennoscandian ice sheet",when:(y,sl)=>iceFrac(y)>.35},
 {lon:12,lat:24,name:"Green Sahara",when:y=>y<14000&&y>6000},{lon:42,lat:34.5,name:"Fertile Crescent",when:y=>y<=11500&&y>3000},{lon:31.2,lat:29,name:"Egypt",when:y=>y<=5200},{lon:46,lat:32.5,name:"Mesopotamia",when:y=>y<=6500&&y>2500},{lon:50.5,lat:27.6,name:"a dry Gulf",when:(y,sl)=>sl<-70}];
PLACES.forEach(p=>{p.x=ax(p.lon);p.yy=ay(p.lat);});
// the valley we follow: its place on Earth moves along humanity's route (mam: woolly mammoths live here)
const VALLEY_PATH=[
 {y:300000,lon:36.4,lat:3.2,name:"the Rift Valley of East Africa"},{y:80000,lon:32.7,lat:25.7,name:"the Nile valley"},{y:62000,lon:35.5,lat:32.9,name:"the Levant"},
 {y:50000,lon:33.5,lat:39.2,name:"Anatolia"},{y:46000,lon:23.5,lat:44.2,name:"the lower Danube",mam:true},{y:36000,lon:16.6,lat:48.9,name:"Moravia, on the mammoth steppe",mam:true},
 {y:26000,lon:1.2,lat:44.9,name:"the Dordogne, in southern France",mam:true},{y:16000,lon:3.2,lat:54.3,name:"Doggerland, between Britain and Europe",mam:true},
 {y:8300,lon:16.4,lat:48.2,name:"the middle Danube"},{y:3600,lon:22.8,lat:37.7,name:"Greece"},{y:2800,lon:12.6,lat:41.8,name:"Latium, in Italy"}];
function valleyAt(y){y=Math.max(0,y);let i=0;while(i<VALLEY_PATH.length-1&&y<=VALLEY_PATH[i+1].y)i++;const a=VALLEY_PATH[i],b=VALLEY_PATH[i+1];
  let lon=a.lon,lat=a.lat;if(b){const span=a.y-b.y,mv=Math.min(4000,span*.2),u=clamp((b.y+mv-y)/mv,0,1),e=u*u*(3-2*u);lon=lerp(a.lon,b.lon,e);lat=lerp(a.lat,b.lat,e);}
  return{lon,lat,x:ax(lon),yy:ay(lat),name:a.name,mam:!!a.mam};}
const JOURNEY=[
 {y:300000,lon:18,lat:4,span:80,text:"300,000 years ago, our species already lives across Africa, from Jebel Irhoud in Morocco to Florisbad in the far south."},
 {y:150000,lon:30,lat:25,span:70,text:"The ice comes and goes, and the seas rise and fall with it. Early ventures reach the Levant, then fade."},
 {y:68000,lon:55,lat:18,span:70,text:"About 70,000 to 60,000 years ago, families leave Africa, following the coasts of Arabia and Asia."},
 {y:56000,lon:120,lat:-6,span:70,text:"The seas are low. Sunda and Sahul are wide land, and people cross open water to reach Australia."},
 {y:42000,lon:18,lat:47,span:55,text:"By about 45,000 years ago, people reach Europe, where mammoths roam the cold steppe."},
 {y:21000,lon:-30,lat:56,span:150,text:"The peak of the last Ice Age. Ice kilometres thick buries the north, and the seas are about 125 metres lower than today."},
 {y:18000,lon:-172,lat:60,span:60,text:"Asia and America are one land: Beringia. People cross into the Americas, perhaps 23,000 to 16,000 years ago."},
 {y:14500,lon:-80,lat:5,span:95,text:"By about 14,500 years ago, families live as far south as Monte Verde in Chile."},
 {y:11200,lon:38,lat:34,span:36,text:"The ice melts. In the Fertile Crescent, people raise the pillars of Göbekli Tepe and begin to farm."},
 {y:8200,lon:4,lat:54,span:26,text:"The rising sea swallows Doggerland, the land that joined Britain to Europe."},
 {y:3850,lon:32,lat:29,span:28,text:"In Egypt, the first alphabet is carved at Wadi el-Hol. Its A is an ox's head."},
 {y:2750,lon:22,lat:39,span:34,text:"The Greeks add vowels, and the Romans shape the letters you are reading now."},
 {y:0,lon:15,lat:25,span:150,text:"And here we are. The Letterheads live through this same history, one day at a time."}];
const ATL={on:false,ready:false,loading:false,img:null,shelfCv:null,iceCv:null,cam:{x:ax(20),y:ay(20),z:.3,tx:ax(20),ty:ay(20),tz:.3},year:null,sel:null,jr:null,
  full:false,fadeT:0,diving:null,shelfK:0,iceK:0,lastLay:0,pull:0};
const atlasCv=document.getElementById("atlasCv"),actx=atlasCv.getContext("2d");
const atlasY=()=>ATL.jr?ATL.jr.year:Math.max(0,ATL.year!=null?ATL.year:yearsAgo());
function atlasResize(){atlasCv.width=W*DPR;atlasCv.height=H*DPR;}
addEventListener("resize",()=>atlasResize());
const aMinZ=()=>Math.max(H/((ALAT0-ALAT1)*AU),W/AMW*.9);
const wrapDX=d=>((d%AMW)+AMW*1.5)%AMW-AMW/2;
const asx=x=>wrapDX(x-ATL.cam.x)*ATL.cam.z+W/2,asy=y=>(y-ATL.cam.y)*ATL.cam.z+H/2;
function atlasInit(){if(ATL.ready||ATL.loading)return;ATL.loading=true;
  const img=new Image();img.onload=()=>{ATL.img=img;maybeReady();};img.src="data:image/jpeg;base64,"+document.getElementById("atlasEarth").textContent.trim();
  const lay=new Image();lay.onload=()=>{const c=document.createElement("canvas");c.width=lay.width;c.height=lay.height;const g=c.getContext("2d",{willReadFrequently:true});g.drawImage(lay,0,0);const d=g.getImageData(0,0,c.width,c.height).data;
    const LW=c.width,LH=c.height,n=LW*LH,R=new Uint8Array(n),G=new Uint8Array(n);for(let i=0;i<n;i++){R[i]=d[i*4];G[i]=d[i*4+1];}
    const sIdx=[],iIdx=[];for(let i=0;i<n;i++){if(R[i])sIdx.push(i);if(G[i])iIdx.push(i);}
    sIdx.sort((a,b)=>R[a]-R[b]);iIdx.sort((a,b)=>G[a]-G[b]);ATL.L={LW,LH,R,G,sIdx:Int32Array.from(sIdx),iIdx:Int32Array.from(iIdx)};
    const mk=()=>{const k=document.createElement("canvas");k.width=LW;k.height=LH;const g2=k.getContext("2d");return{c:k,g:g2,d:g2.createImageData(LW,LH)};};
    ATL.shelf=mk();ATL.ice=mk();for(const l of[ATL.shelf,ATL.ice]){l.soft=document.createElement("canvas");l.soft.width=LW;l.soft.height=LH;l.sg=l.soft.getContext("2d");}ATL.comb=document.createElement("canvas");ATL.comb.width=LW;ATL.comb.height=LH;ATL.cg=ATL.comb.getContext("2d");ATL.shelfK=0;ATL.iceK=0;maybeReady();};
  lay.src="data:image/png;base64,"+document.getElementById("atlasLayers").textContent.trim();
  function maybeReady(){if(ATL.img&&ATL.L){ATL.ready=true;ATL.loading=false;atlasLayers(true);atlasCard();}}}
function soften(l){l.g.putImageData(l.d,0,0);const g=l.sg;g.clearRect(0,0,l.soft.width,l.soft.height);try{g.filter="blur(0.9px)";}catch(e){}g.drawImage(l.c,0,0);g.filter="none";}
const hash01=i=>{let h=Math.imul(i^0x9E3779B9,0x85EBCA6B);h^=h>>>13;h=Math.imul(h,0xC2B2AE35);h^=h>>>16;return(h>>>0)/4294967296;};
const SHELF_BANDS=[[0,[88,110,56]],[15,[120,122,70]],[25,[160,144,98]],[40,[148,138,102]],[55,[134,132,108]],[70,[166,164,152]],[90,[176,176,168]]];
function shelfColor(i){const L=ATL.L,r=(i/L.LW)|0,lat=Math.abs(90-(r+.5)*180/L.LH);let c=SHELF_BANDS[0][1];
  for(let k=1;k<SHELF_BANDS.length;k++)if(lat<=SHELF_BANDS[k][0]){const[a0,c0]=SHELF_BANDS[k-1],[a1,c1]=SHELF_BANDS[k];const u=(lat-a0)/(a1-a0);c=[0,1,2].map(j=>c0[j]+(c1[j]-c0[j])*u);break;}
  const n=.92+hash01(i)*.14,shore=1+(1-L.R[i]/250)*.08;return[c[0]*n*shore,c[1]*n*shore,c[2]*n*shore];}
// paint only the pixels that changed since last time: sorted by depth (shelf) or by distance from the ice centre (ice)
function atlasLayers(force){if(!ATL.ready)return;const y=atlasY(),L=ATL.L;if(!force&&performance.now()-ATL.lastLay<90)return;ATL.lastLay=performance.now();
  const sl=Math.min(0,seaLevel(y)),code=-sl/.6;let lo=0,hi=L.sIdx.length;while(lo<hi){const m=(lo+hi)>>1;if(L.R[L.sIdx[m]]<code)lo=m+1;else hi=m;}const kS=lo;
  const f=iceFrac(y),gc=1+f*254;lo=0;hi=L.iIdx.length;while(lo<hi){const m=(lo+hi)>>1;if(L.G[L.iIdx[m]]<gc)lo=m+1;else hi=m;}const kI=f<=0?0:lo;
  const paint=(lay,idx,k0,k1,on,col)=>{const d=lay.d.data;for(let j=Math.min(k0,k1);j<Math.max(k0,k1);j++){const i=idx[j],p=i*4;if(on){const c=col(i);d[p]=c[0];d[p+1]=c[1];d[p+2]=c[2];d[p+3]=c[3]??255;}else d[p+3]=0;}};
  const was=ATL.shelfK+"|"+ATL.iceK;
  if(kS!==ATL.shelfK){paint(ATL.shelf,L.sIdx,ATL.shelfK,kS,kS>ATL.shelfK,shelfColor);ATL.shelfK=kS;soften(ATL.shelf);}
  if(kI!==ATL.iceK){paint(ATL.ice,L.iIdx,ATL.iceK,kI,kI>ATL.iceK,i=>{const n=hash01(i*7)*10-5,e=L.G[i]/255;return[232+n-e*10,240+n-e*6,247+n,246-e*20];});ATL.iceK=kI;soften(ATL.ice);}
  if(force||was!==ATL.shelfK+"|"+ATL.iceK){const g=ATL.cg;g.clearRect(0,0,L.LW,L.LH);g.drawImage(ATL.shelf.soft,0,0);g.drawImage(ATL.ice.soft,0,0);}}
let glowSprite=null;function glow(){if(glowSprite)return glowSprite;const c=document.createElement("canvas");c.width=c.height=48;const g=c.getContext("2d");const gr=g.createRadialGradient(24,24,1,24,24,24);
  gr.addColorStop(0,"rgba(255,214,140,1)");gr.addColorStop(.18,"rgba(240,160,60,.9)");gr.addColorStop(.5,"rgba(232,150,47,.28)");gr.addColorStop(1,"rgba(232,150,47,0)");g.fillStyle=gr;g.fillRect(0,0,48,48);return glowSprite=c;}
function aLabel(text,x,y,o){const g=actx;g.font=o.font||"italic 600 15px Spectral, Georgia, serif";g.textAlign=o.align||"center";g.textBaseline="middle";g.lineJoin="round";g.lineWidth=4;g.strokeStyle=o.halo||"rgba(6,14,30,.75)";g.strokeText(text,x,y);g.fillStyle=o.col||"#F4EFE2";g.fillText(text,x,y);}
function atlasDraw(dt){const g=actx,c=ATL.cam,z=c.z,y=atlasY(),sl=seaLevel(y),t=tAnim;
  g.setTransform(DPR,0,0,DPR,0,0);g.fillStyle="#051233";g.fillRect(0,0,W,H);if(!ATL.ready){aLabel("Loading the Earth…",W/2,H/2,{font:"600 18px 'Atkinson Hyperlegible', sans-serif"});return;}
  atlasLayers(false);g.imageSmoothingEnabled=true;g.imageSmoothingQuality="high";const top=(0-c.y)*z+H/2;
  for(let k=-1;k<=1;k++){const ox=(k*AMW-c.x)*z+W/2;if(ox>W||ox+AMW*z<0)continue;g.drawImage(ATL.img,ox,top,AMW*z,AMH*z);
    if(y<14500&&y>5000){const a=.22*Math.min(clamp((14500-y)/2000,0,1),clamp((y-5000)/1500,0,1));const cx=ox+ax(12)*z,cy=top+ay(21)*z,rx=38*AU*z,ry=10*AU*z;g.save();g.translate(cx,cy);g.scale(1,ry/rx);const gr=g.createRadialGradient(0,0,0,0,0,rx);gr.addColorStop(0,`rgba(96,128,58,${a})`);gr.addColorStop(.7,`rgba(96,128,58,${a*.7})`);gr.addColorStop(1,"rgba(96,128,58,0)");g.fillStyle=gr;g.fillRect(-rx,-rx,rx*2,rx*2);g.restore();}
    g.drawImage(ATL.comb,ox,top,AMW*z,AMH*z);}
  // places that matter now
  for(const p of PLACES)if(p.when(y,sl))aLabel(p.name,asx(p.x),asy(p.yy),{font:"italic 600 "+(z>.9?17:14)+"px Spectral, Georgia, serif",col:"#E9E4D6"});
  // routes, then clusters of Letterheads
  g.lineCap="round";const gl=glow();
  for(const n of NODES){if(!n.from)continue;const p=NODE[n.from];if(y>p.y)continue;const st=Math.min(p.y,n.y+Math.max(3000,n.y*.15));const u=clamp((st-y)/(st-n.y),0,1);if(u<=0)continue;
    const x0=asx(p.x),y0=asy(p.yy),x1=x0+wrapDX(n.x-p.x)*z,y1=asy(n.yy);const mx=(x0+x1)/2+(y1-y0)*.12,my=(y0+y1)/2-(x1-x0)*.12;
    const q=(s,a,b,m)=>(1-s)*(1-s)*a+2*(1-s)*s*m+s*s*b;g.setLineDash([2,6]);g.strokeStyle="rgba(242,196,120,.75)";g.lineWidth=1.6;g.beginPath();g.moveTo(x0,y0);const N=24;for(let i=1;i<=N*u;i++){const s=i/N;g.lineTo(q(s,x0,x1,mx),q(s,y0,y1,my));}g.lineTo(q(u,x0,x1,mx),q(u,y0,y1,my));g.stroke();g.setLineDash([]);
    if(u<1){const hx=q(u,x0,x1,mx),hy=q(u,y0,y1,my);g.drawImage(gl,hx-10,hy-10,20,20);}}
  for(const n of NODES){if(y>n.y)continue;const sx=asx(n.x),sy=asy(n.yy);if(sx<-60||sx>W+60||sy<-60||sy>H+60)continue;const age=n.y-y,cnt=3+Math.floor(9*clamp(age/(n.y*.5+3000),0,1)),r=6+cnt*.9;
    for(let i=0;i<cnt;i++){const a=hash01(i*31+n.x)*6.283,d=r*Math.sqrt(hash01(i*17+n.yy)),w=S.settings.reduce?0:Math.sin(t*.7+i*1.7)*1.5;const s=14+hash01(i*5+n.x)*9;g.globalAlpha=.9;g.drawImage(gl,sx+Math.cos(a)*d+w-s/2,sy+Math.sin(a)*d-s/2,s,s);}g.globalAlpha=1;g.fillStyle="#FFE2A8";g.beginPath();g.arc(sx,sy,2.2,0,Math.PI*2);g.fill();
    if(ATL.sel&&ATL.sel.n===n){g.setLineDash([5,5]);g.strokeStyle="#E8962F";g.lineWidth=2;g.beginPath();g.arc(sx,sy,r+14,0,Math.PI*2);g.stroke();g.setLineDash([]);}
    if(z>.55||age<Math.max(4000,n.y*.12)||(ATL.sel&&ATL.sel.n===n))aLabel(n.name.replace(/^the families of /,""),sx,sy+r+20,{font:"600 12px 'Atkinson Hyperlegible', sans-serif",col:"#FCE3BA"});}
  // events: fresh ones are named; older ones stay as small marks
  for(const e of EVENTS){if(y>e.y)continue;const sx=asx(e.x),sy=asy(e.yy);if(sx<-80||sx>W+80||sy<-40||sy>H+40)continue;const fresh=e.y-y<Math.max(1200,e.y*.18),selE=ATL.sel&&ATL.sel.e===e;
    g.save();g.translate(sx,sy);g.rotate(Math.PI/4);g.fillStyle=fresh||selE?"#F6F1E4":"rgba(246,241,228,.55)";g.strokeStyle="#1F2421";g.lineWidth=1.4;const s=fresh||selE?9:6;g.fillRect(-s/2,-s/2,s,s);g.strokeRect(-s/2,-s/2,s,s);g.restore();
    if(fresh||selE||z>1.3)aLabel(e.name,sx+10,sy,{align:"left",font:(fresh||selE?"700 13px":"400 12px")+" 'Atkinson Hyperlegible', sans-serif",col:fresh||selE?"#FFFFFF":"#DAD6CB"});}
  // the valley we follow
  {const v=valleyAt(y),sx=asx(v.x),sy=asy(v.yy),pu=S.settings.reduce?0:(Math.sin(t*2.2)+1)/2;g.strokeStyle="#FFFFFF";g.lineWidth=2;g.beginPath();g.arc(sx,sy,11+pu*5,0,Math.PI*2);g.stroke();g.fillStyle="#E8962F";g.beginPath();g.arc(sx,sy,6.5,0,Math.PI*2);g.fill();
    g.strokeStyle="#1F2421";g.lineWidth=1.5;g.stroke();aLabel("The valley we follow",sx,sy-24,{font:"700 13px 'Atkinson Hyperlegible', sans-serif",col:"#FFFFFF"});ATL.vs={x:sx,y:sy};}
  if(ATL.diving){const k=clamp((tAnim-ATL.diving.t0)/1.3,0,1);if(k>.55){g.fillStyle=`rgba(213,219,200,${(k-.55)/.45})`;g.fillRect(0,0,W,H);}}}
function atlasCam(dt){const c=ATL.cam,red=S.settings.reduce;
  if(ATL.jr)journeyTick(dt);
  else{const k=red?1:1-Math.exp(-dt*2.2);const dx=wrapDX(c.tx-c.x);c.x+=dx*k;c.y=lerp(c.y,c.ty,k);c.z=Math.exp(lerp(Math.log(c.z),Math.log(c.tz),k));}
  c.z=clamp(c.z,aMinZ(),2.6);c.tz=clamp(c.tz,aMinZ(),2.6);c.x=((c.x%AMW)+AMW)%AMW;const hh=H/2/c.z,y0=ay(ALAT0)+hh,y1=ay(ALAT1)-hh;c.y=y0>y1?(ay(ALAT0)+ay(ALAT1))/2:clamp(c.y,y0,y1);}
const cardLift=()=>Math.min(170,H*.2)/ATL.cam.tz;
function spanZ(deg){return clamp(Math.min(W,H*1.6)/(deg*AU),aMinZ(),2.6);}
function flyTo(lon,lat,deg){const c=ATL.cam;c.tx=ax(lon);c.tz=spanZ(deg);c.ty=ay(lat)+cardLift();}
function journeyTick(dt){const J=ATL.jr,st=JOURNEY[J.i],c=ATL.cam,red=S.settings.reduce;J.t+=dt;const fl=Math.min(3.4,st.dur*.45),u=red?1:clamp(J.t/fl,0,1),e=easeIO(u);
  const tz=spanZ(st.span),tx=ax(st.lon),ty=ay(st.lat)+Math.min(170,H*.2)/tz;const d=Math.hypot(wrapDX(tx-J.from.x),ty-J.from.y);const dip=red?0:Math.min(.45,d/AMW*1.6)*Math.sin(Math.PI*e);
  c.x=J.from.x+wrapDX(tx-J.from.x)*e;c.y=lerp(J.from.y,ty,e);c.z=Math.exp(lerp(Math.log(J.from.z),Math.log(tz),e))*(1-dip);c.tx=c.x;c.ty=c.y;c.tz=c.z;
  J.year=Math.max(0,Math.exp(lerp(Math.log(J.from.year+60),Math.log(st.y+60),e))-60);
  if(J.t>=st.dur){if(J.i>=JOURNEY.length-1){endJourney();return;}J.i++;J.t=0;J.from={x:c.x,y:c.y,z:c.z,year:J.year};JOURNEY[J.i].dur=JOURNEY[J.i].dur||8;journeyCard();}}
function startJourney(){atlasIntroCancel();if(!ATL.ready)return;ATL.sel=null;const c=ATL.cam;JOURNEY.forEach(s=>s.dur=s.text.length>110?9:8);ATL.jr={i:0,t:0,from:{x:c.x,y:c.y,z:c.z,year:atlasY()},year:atlasY()};document.body.classList.add("journey");journeyCard();if(Music.on)Music.built();}
function endJourney(){ATL.jr=null;ATL.year=null;document.body.classList.remove("journey");const v=valleyAt(atlasY());flyTo(v.lon,v.lat,50);atlasCard();}
function journeyCard(){const st=JOURNEY[ATL.jr.i];setTimeout(placeAtlasZoom,0);document.getElementById("atlasTitle").textContent=st.y?`Earth, ${yearLabel(st.y)}`:"Earth, today";document.getElementById("atlasSub").textContent=st.text;}
function seaText(sl){const m=Math.round(-sl/5)*5;return m>=10?`Seas are about ${m} metres lower than today.`:sl>2?"Seas are a few metres higher than today.":"Seas are near today's level.";}
function atlasCard(){if(ATL.jr)return;const tEl=document.getElementById("atlasTitle"),sEl=document.getElementById("atlasSub"),y=atlasY(),sl=seaLevel(y);
  document.getElementById("atlasSelClose").hidden=!ATL.sel;
  const src=s=>s?` Source: ${s[0]}${s[2]?" (checked through Anakin's research tools)":" (to be verified by experts)"}.`:"";
  if(!ATL.ready){tEl.textContent="The Atlas";sEl.textContent="Loading the real Earth…";return;}
  if(ATL.sel&&ATL.sel.n){const n=ATL.sel.n;tEl.textContent=n.name[0].toUpperCase()+n.name.slice(1);sEl.textContent=`${n.when}. ${n.text}${src(n.src)}`;}
  else if(ATL.sel&&ATL.sel.e){const e=ATL.sel.e;tEl.textContent=e.name;sEl.textContent=`About ${yearLabel(e.y)}. ${e.text}${src(e.src)}`;}
  else if(ATL.sel&&ATL.sel.v){const v=valleyAt(y);tEl.textContent="The valley we follow";sEl.textContent=`It lies in ${v.name}. ${S.agents.length} letters and ${(n=>n+(n===1?" word":" words"))(S.words.filter(w=>w.state!=="forming").length)} live there now. Its hills, rivers, coasts and ground are the real ones${(()=>{const P=typeof placeNow==="function"&&TERRA_READY?placeNow():null;return P&&P.veg?". In this era it was "+P.veg.split(" Source")[0].replace(/\s*\([^)]*\)/g,"").replace(/^./,c=>c.toLowerCase()):".";})()} The letters, trees and stones are the game's own. As history moves on, the valley moves along humanity's route.`;}
  else{const live=ATL.year==null,reached=NODES.filter(n=>y<=n.y).length;tEl.textContent=`Earth, ${yearLabel(y)}`;
    sEl.textContent=`${seaText(sl)}${iceFrac(y)>.35?" Great ice sheets cover the north.":""} Letterheads live in ${reached} region${reached===1?"":"s"}. The valley we follow is in ${valleyAt(y).name}.`;}
  const r=document.getElementById("atlasTime");if(document.activeElement!==r)r.value=Math.round(monthOf(y)/36*1000);document.getElementById("atlasWhen").textContent=ATL.year==null?"Now in this world":yearLabel(y);document.getElementById("atlasNow").hidden=ATL.year==null;placeAtlasZoom();}
function placeAtlasZoom(){const c=document.querySelector(".acard"),z=document.querySelector(".azoom");if(c&&z)z.style.bottom=(innerHeight-c.getBoundingClientRect().top+14)+"px";}
function monthOf(y){for(const[m0,m1,y0,y1]of HIST_SEG)if(y>=y1)return lerp(m0,m1,(y0-y)/(y0-y1));return 36;}
function yearOfMonth(m){for(const[m0,m1,y0,y1]of HIST_SEG)if(m<=m1)return lerp(y0,y1,(m-m0)/(m1-m0));return 0;}
function openAtlas(){if(ATL.on)return;if(tour)endTour(false);closeSheet();ATL.on=true;ATL.full=false;ATL.diving=null;ATL.pull=0;atlasResize();atlasInit();document.body.classList.add("atlas-on");atlasCv.classList.add("on");
  const v=valleyAt(atlasY()),c=ATL.cam;c.x=v.x;c.y=v.yy;c.z=2.6;flyTo(v.lon,v.lat,100);ATL.sel=null;ATL.fadeT=tAnim;atlasCard();S.settings.atlasSeen=true;save();
  document.getElementById("atlasDive").focus({preventScroll:true});}
function closeAtlas(now){if(!ATL.on)return;ATL.on=false;ATL.full=false;ATL.diving=null;if(ATL.jr){ATL.jr=null;document.body.classList.remove("journey");}document.body.classList.remove("atlas-on");atlasCv.classList.remove("on");
  if(!now){cam.z=minZ();cam.mode=S.settings.camera==="fixed"?"free":"director";}updateCaption();}
function diveIn(){if(!ATL.on||ATL.diving)return;const v=valleyAt(atlasY());if(ATL.jr)endJourney();ATL.sel=null;ATL.year=null;const c=ATL.cam;c.tx=v.x;c.ty=v.yy;c.tz=2.6;ATL.diving={t0:tAnim};
  setTimeout(()=>{closeAtlas(false);},S.settings.reduce?50:1300);}
function atlasFrame(dt){if(!ATL.full&&tAnim-ATL.fadeT>1)ATL.full=true;atlasCam(dt);const t0=performance.now();atlasDraw(dt);ATL.ms=(ATL.ms||0)*.9+(performance.now()-t0)*.1;if(tAnim>=(ATL.nextCard||0)){ATL.nextCard=tAnim+.5;atlasCard();}}
function atlasHit(px,py){const y=atlasY();if(ATL.vs&&Math.hypot(px-ATL.vs.x,py-ATL.vs.y)<26)return{v:true};let best=null,bd=26;
  for(const n of NODES){if(y>n.y)continue;const d=Math.hypot(px-asx(n.x),py-asy(n.yy));if(d<bd){bd=d;best={n};}}
  for(const e of EVENTS){if(y>e.y)continue;const d=Math.hypot(px-asx(e.x),py-asy(e.yy));if(d<bd*.8){bd=d/.8;best={e};}}return best;}
{const ptr=new Map();let dr=null;
  atlasCv.addEventListener("pointerdown",e=>{atlasCv.setPointerCapture(e.pointerId);ptr.set(e.pointerId,{x:e.clientX,y:e.clientY});dr={x:e.clientX,y:e.clientY,cx:ATL.cam.x,cy:ATL.cam.y,moved:false,pd:0};});
  atlasCv.addEventListener("pointermove",e=>{if(!ptr.has(e.pointerId)||!dr||ATL.jr||ATL.diving)return;ptr.set(e.pointerId,{x:e.clientX,y:e.clientY});const c=ATL.cam;
    if(ptr.size===2){const[p1,p2]=[...ptr.values()];const d=Math.hypot(p1.x-p2.x,p1.y-p2.y);if(dr.pd){c.z=c.tz=clamp(c.z*d/dr.pd,aMinZ(),2.6);}dr.pd=d;dr.moved=true;return;}
    const dx=e.clientX-dr.x,dy=e.clientY-dr.y;if(Math.hypot(dx,dy)>6)dr.moved=true;if(dr.moved){c.x=c.tx=dr.cx-dx/c.z;c.y=c.ty=dr.cy-dy/c.z;}});
  atlasCv.addEventListener("pointerup",e=>{ptr.delete(e.pointerId);if(dr&&!dr.moved&&!ATL.jr&&!ATL.diving){const h=atlasHit(e.clientX,e.clientY);
      if(h&&h.v){if(ATL.sel&&ATL.sel.v)diveIn();else{ATL.sel=h;const v=valleyAt(atlasY());flyTo(v.lon,v.lat,Math.min(40,W/ATL.cam.tz/AU));}}
      else if(h){ATL.sel=h;const o=h.n||h.e;ATL.cam.tx=o.x;ATL.cam.tz=Math.max(ATL.cam.z,spanZ(45));ATL.cam.ty=o.yy+cardLift();}else ATL.sel=null;atlasCard();}
    if(!ptr.size)dr=null;});
  atlasCv.addEventListener("wheel",e=>{e.preventDefault();if(ATL.jr||ATL.diving)return;const c=ATL.cam,mx=(e.clientX-W/2)/c.z+c.x,my=(e.clientY-H/2)/c.z+c.y;const nz=clamp(c.z*Math.exp(-e.deltaY*.0015),aMinZ(),2.6);
    if(e.deltaY<0&&c.z>=2.59){ATL.pull+=-e.deltaY;if(ATL.pull>400){ATL.pull=0;diveIn();}return;}ATL.pull=0;c.x=c.tx=mx-(e.clientX-W/2)/nz;c.y=c.ty=my-(e.clientY-H/2)/nz;c.z=c.tz=nz;},{passive:false});
  atlasCv.addEventListener("keydown",e=>{const c=ATL.cam,st=60/c.z;if(e.key==="ArrowLeft")c.tx-=st;if(e.key==="ArrowRight")c.tx+=st;if(e.key==="ArrowUp")c.ty-=st;if(e.key==="ArrowDown")c.ty+=st;if(e.key==="+"||e.key==="=")c.tz*=1.2;if(e.key==="-")c.tz/=1.2;if(e.key==="Escape")diveIn();});}
document.getElementById("atlasBtn").onclick=()=>ATL.on?diveIn():openAtlas();
document.getElementById("atlasDive").onclick=diveIn;
document.getElementById("atlasJourney").onclick=startJourney;
document.getElementById("atlasStop").onclick=endJourney;
document.getElementById("atlasInfo").onclick=()=>openOurWorld(Math.max(.5,atlasY()));
document.getElementById("atlasSelClose").onclick=()=>{ATL.sel=null;atlasCard();};
document.getElementById("atlasNow").onclick=()=>{ATL.year=null;atlasCard();};
document.getElementById("atlasTime").oninput=e=>{ATL.sel=null;ATL.year=Math.max(0,yearOfMonth(+e.target.value/1000*36));atlasCard();};
document.getElementById("atlasIn").onclick=()=>{ATL.cam.tz=clamp(ATL.cam.tz*1.3,aMinZ(),2.6);};
document.getElementById("atlasOut").onclick=()=>{ATL.cam.tz=clamp(ATL.cam.tz/1.3,aMinZ(),2.6);};
