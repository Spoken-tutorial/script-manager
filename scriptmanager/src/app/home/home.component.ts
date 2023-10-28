import { Component, OnInit } from '@angular/core';
import { FossService } from '../_service/foss.service';
import { TutorialsService } from '../_service/tutorials.service'
import { AuthService } from '../_service/auth.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.sass']
})
export class HomeComponent implements OnInit {
  public sourceData;
  public domainCategories = ['spokentutorials', 'healthnutrition'];
  public currentDomainCategory : string ='';
  public fossCategories;
  public currentFossCategory = -1;
  public languages;
  public currentLanguage = -1;
  public tutorials;
  public description: string = '';

  constructor(
    public fossService: FossService,
    public tutorialService: TutorialsService,
    public authService: AuthService
  ) { }


  public onDomainCategoryChange(name){
    this.currentDomainCategory = name;
    localStorage.setItem("domain",name);
    this.fossCategories = this.sourceData[name]['foss']
    this.currentFossCategory = -1
    this.currentLanguage = -1
    this.description =''
    this.tutorials = null
  }

  public onFossCategoryChange(fid) {
    this.currentFossCategory = fid;
    localStorage.setItem("fid",fid);
    this.languages = this.sourceData[this.currentDomainCategory]['language']
    this.currentLanguage = -1
    this.tutorials = null
    for(let i=0; i < this.fossCategories.length; i++){
      if (this.fossCategories[i]['id'] == fid){
        this.description = this.fossCategories[i]['description'];
        break;
      }
    }

  }

  public onLanguageChange(lid) {
    localStorage.setItem("lid",lid);
    if(this.currentFossCategory != -1 && lid != -1){
    this.currentLanguage = lid;
    this.fetchTutorials(this.currentDomainCategory,this.currentFossCategory,this.currentLanguage);
    }
  }

  public fetchAllFoss() {
    this.fossService.getAllFossCategories().subscribe(
      (res) => {
        this.sourceData = res['data'];
      },
      (err) => {
        console.error('Failed to fetch foss categories', err);
      }
    );
  }

  public fetchTutorials(domain,fossId, languageId) {
    this.tutorialService.getFossTutorials(domain, fossId, languageId).subscribe(
      (res) => this.tutorials = res['data']['tutorials'],
      console.error
    );
  }

  ngOnInit() {
    this.fetchAllFoss();
    if(localStorage.getItem("domain")){
      let name = localStorage.getItem("domain");
      let fid = localStorage.getItem("fid");
      this.fossService.getAllFossCategories().subscribe(
        (res) => {
          this.sourceData = res['data'];
          this.fossCategories = this.sourceData[name]['foss'];
          this.languages = this.sourceData[name]['language']
          for(let i=0; i < this.fossCategories.length; i++){
            if (this.fossCategories[i]['id'] == fid){
              this.description = this.fossCategories[i]['description'];
              break;
            }
          }
          this.currentDomainCategory = name;
          this.currentFossCategory = parseInt(fid);
          this.currentLanguage = parseInt(localStorage.getItem("lid"));

          this.tutorialService.getFossTutorials(name, fid, this.currentLanguage).subscribe(
            (res) => this.tutorials = res['data']['tutorials'],
            console.error
          );
        },
        (err) => {
          console.error('Failed to fetch foss categories', err);
        }
      );



    }
  };

}
