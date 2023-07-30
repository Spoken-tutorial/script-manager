import { Component, OnInit } from '@angular/core';
import { CreateScriptService } from 'src/app/_service/create-script.service';

@Component({
  selector: 'app-published-scripts',
  templateUrl: './published-scripts.component.html',
  styleUrls: ['./published-scripts.component.sass']
})
export class PublishedScriptsComponent implements OnInit {
  public scripts: any = [];

  constructor(
    private createScriptService: CreateScriptService
  ) { }

  ngOnInit() {
    this.createScriptService.getPublishedScripts().subscribe(
      (res) => {
        this.scripts = res['data'];
      },
      console.error
    )
  }

}
