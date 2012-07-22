/*
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */
package de.dekstop.cosm;

import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import javax.imageio.ImageIO;

import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.joda.time.Days;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;
import org.joda.time.Hours;
import org.joda.time.Minutes;
import org.joda.time.Seconds;

/**
 *
 */
public class Coverage {

  private static String imageFormat = "png";
  private static String defaultDateFormat = "yyyy-MM-dd HH:mm:ss";
  
  public static enum CoverageType {
    SECOND,
    MINUTE,
    HOUR,
    DAY
  };
  
  /**
   *
   */
  public static interface Parser<T> {

    public abstract T parse(String line) throws ParseException;

  }
  
  /**
   *
   */
  public static class FileImporter<T> {

    Parser<T> parser = null;

    public FileImporter(Parser<T> parser) {
      this.parser = parser;
    }

    public List<T> parse(File file) throws IOException, ParseException {
      BufferedReader reader = new BufferedReader(new FileReader(file));
      List<T> data = new ArrayList<T>();
      String line = reader.readLine();
      while(line != null) {
        data.add(parser.parse(line));
        line = reader.readLine();
      }
      reader.close();
      return data;
    }

  }
  
  /**
   * 
   */
  public static class TaggedDateTime {
      public String tag;
      public DateTime date;
  }
  
  /**
   *
   */
  public static class TaggedDateParser implements Parser<TaggedDateTime> {

    DateTimeFormatter formatter;

    public TaggedDateParser(String dateFormatPattern) {
      formatter = DateTimeFormat.forPattern(dateFormatPattern).withZone(DateTimeZone.UTC);
    }

    @Override
    public TaggedDateTime parse(String line) throws ParseException {
      String[] columns = line.split("\t");
      if (columns.length!=2) {
        throw new ParseException("Wrong number of columns: " + line, 0);
      }
      TaggedDateTime td = new TaggedDateTime();
      td.tag = columns[0];
      td.date = formatter.parseDateTime(columns[1]);
      return td;
    }
  }
  
  static CoverageType getType(String str) {
    if (str==null) return null;
    try {
      return CoverageType.valueOf(str.toUpperCase());
    } catch (IllegalArgumentException e) {
      return null;
    }
  }
  
  static int getDistance(CoverageType type, DateTime start, DateTime end) {
    switch (type) {
      case SECOND: return Seconds.secondsBetween(start, end).getSeconds();
      case MINUTE: return Minutes.minutesBetween(start, end).getMinutes();
      case HOUR: return Hours.hoursBetween(start, end).getHours();
      case DAY: return Days.daysBetween(start, end).getDays();
    }
    throw new IllegalArgumentException("Unknown type: " + type);
  }

  /**
   * @param args
   */
  public static void main(String[] args) throws Exception {
    if (args.length < 3 || args.length > 4) {
      System.out.println("<second|minute|hour|day> <data-filename> <output-dir> [format]");
      System.out.println("File format is tab-separated text: <tag> <timestamp>");
      System.out.println("Reads ISO timestamps by default: yyyy-MM-dd HH:mm:ss");
      System.out.println("Output order reflects the order of tags in input data.");
      System.exit(1);
    }
    
    // Args
    CoverageType type = getType(args[0]);
    if (type==null) {
      System.out.println("Can't determine coverage type: " + args[0] + " Reverting to default type.");
      type = CoverageType.DAY;
    }
    String dataFilename = args[1];
    String outputDirname = args[2];
    String dateFormat = defaultDateFormat;
    if (args.length==4) {
      dateFormat = args[3];
    }
    
    File dataFile = new File(dataFilename);
    
    String name = dataFile.getName();
    if (name.lastIndexOf('.')!=-1) {
      name = name.substring(0, name.lastIndexOf('.'));
    }
    File imageFile = new File(outputDirname, String.format(
      "%s-%s.%s", name, type.toString().toLowerCase(), imageFormat));
    System.out.println(imageFile.getName() + " ...");
    
    File outputDir = new File(outputDirname);
    if (!outputDir.exists()) {
      outputDir.mkdirs();
    }
    
    // Load data
    // 2011-11-06T06:14:32.656171Z
    List<TaggedDateTime> records = new FileImporter<TaggedDateTime>(new TaggedDateParser(dateFormat)).parse(dataFile);
    HashMap<String, List<DateTime>> entries = new HashMap<String, List<DateTime>>();
    List<String> entryOrder = new ArrayList<String>();
    DateTime minDate = records.get(0).date;
    DateTime maxDate = records.get(0).date;
    for (TaggedDateTime record : records) {
      if (!entries.containsKey(record.tag)) {
        entryOrder.add(record.tag);
        entries.put(record.tag, new ArrayList<DateTime>());
      }
      entries.get(record.tag).add(record.date);
      minDate = record.date.compareTo(minDate) < 0 ? record.date : minDate;
      maxDate = record.date.compareTo(maxDate) >= 0 ? record.date : maxDate;
    }
    System.out.println(String.format("Loaded %d records for %d tags.", records.size(), entries.size()));
    DateTimeFormatter df = DateTimeFormat.forPattern(defaultDateFormat).withZone(DateTimeZone.UTC);
    System.out.println(String.format("First date: %s", df.print(minDate)));
    System.out.println(String.format("Last date: %s", df.print(maxDate)));
    
    // Image
    int width = getDistance(type, minDate, maxDate) + 1;
    int height = entries.size();
    
    System.out.println(String.format("Image dimensions: %d x %d", width, height));

    BufferedImage img = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
    
    int y = 0;
    for (String tag : entryOrder) {
      for (DateTime date : entries.get(tag)) {
        int x = getDistance(type, minDate, date);
        img.setRGB(x, y, 0x0ffffffff);
      }
      y++;
    }
    // Graphics2D g2 = img.createGraphics();
    // g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
    
    // Write to file
    ImageIO.write(img, imageFormat, imageFile);
  }
}
